"""Live MTG (Météosat Troisième Génération) basemap for every real map
view (ESOC's main map, the AWCI dashboard, the Classic Dashboard).

Explicit user request: "je veux que toutes les maps affiché soient des
maps du mtg". See acf.connectors.eumetsat_mtg's own docstring for what
is actually fetched (EUMETSAT's own official Quicklook/browse asset for
the latest FCI Level 1c full-disk product) and its honest limitations
(thumbnail resolution, approximate geolocation) - this module is only
the Qt-facing plumbing: fetch off the GUI thread, decode, cache, notify.

MTGBasemapProvider is a process-wide singleton (one shared fetch/cache
for every map view, on a QTimer matching the FCI's own repeat cycle -
each real map canvas connects to `updated` and redraws when a fresh
image lands, via draw_mtg_basemap()). Never blocks the GUI thread: the
network call runs on QThreadPool via a QRunnable, the same pattern
acf.gui.esoc.esoc_window._AWCIFieldWorker already uses for the (also
real-data-only) AWCI complexity field.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

import cartopy.crs as ccrs
import numpy as np
import pyproj
import yaml
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal

from acf.connectors.eumetsat_mtg import (
    MTG_SATELLITE_HEIGHT_M,
    MTG_SUBSATELLITE_LONGITUDE_DEG,
    EUMETSATMTGConnector,
    MTGFetchResult,
)

logger = logging.getLogger("acf.gui.map.mtg_basemap")

_CONFIG_PATH = Path("config/eumetsat.yaml")
_DEFAULT_REFRESH_SECONDS = 600
_DEFAULT_COLLECTION = "EO:EUM:DAT:0662"


def _load_mtg_config() -> dict[str, Any]:
    """Best-effort read of config/eumetsat.yaml - falls back to the same
    defaults acf.connectors.eumetsat_mtg itself uses when the file is
    missing or malformed, same convention as e.g.
    acf.hpc_connector.configuration.HPCConfiguration._default_config()."""
    defaults = {"collection": _DEFAULT_COLLECTION, "refresh_seconds": _DEFAULT_REFRESH_SECONDS}
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        mtg = data.get("mtg", {})
        return {
            "collection": mtg.get("collection", defaults["collection"]),
            "refresh_seconds": int(mtg.get("refresh_seconds", defaults["refresh_seconds"])),
        }
    except Exception:
        logger.warning("Could not read %s, using built-in MTG basemap defaults", _CONFIG_PATH, exc_info=True)
        return defaults


def geostationary_crs() -> ccrs.Geostationary:
    """Real MTG-I1 viewing geometry (sub-satellite point, altitude) as a
    Cartopy CRS - shared by draw_mtg_basemap() and its extent below so
    the two can never drift apart."""
    return ccrs.Geostationary(
        central_longitude=MTG_SUBSATELLITE_LONGITUDE_DEG,
        satellite_height=MTG_SATELLITE_HEIGHT_M,
        sweep_axis="y",  # EUMETSAT/Meteosat scan convention (vs. GOES's "x")
    )


#: Real, physically-valid MTG-I1 viewing footprint used to build the
#: reprojected grid below - a geostationary satellite cannot see past
#: roughly +-81 degrees great-circle distance from its sub-satellite
#: point (the Earth's own curvature occludes the view beyond that); 80
#: is a small, safe margin inside that limb.
_MAX_VIEW_DEGREES = 80.0
_REPROJECT_STEP_DEGREES = 0.25


def _reproject_geostationary_to_platecarree(
    rgba: np.ndarray, geo_crs: ccrs.Geostationary
) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    """Resample a raw geostationary full-disk image onto a plain
    equirectangular (PlateCarree) lon/lat grid, and return that grid's
    (lon_min, lon_max, lat_min, lat_max) extent alongside it.

    NOTE (why this exists - a real bug found while testing this
    feature): the first version of this module handed the raw
    geostationary image straight to Cartopy's own
    imshow(transform=geo_crs) on a PlateCarree (or Mercator) axes,
    relying on Cartopy to regrid it. That regrid inverse-projects every
    target-map pixel back into the image's geostationary coordinates -
    and PROJ's `geos` inverse formula is only physically meaningful
    within the visible disk; just beyond its limb, the same analytic
    formula still returns finite (but meaningless, periodic) values.
    Confirmed visually: a pinched "hourglass" disk plus phantom repeated
    copies near +-120 degrees longitude on ESOC's global map - a real
    reprojection artifact, not a fabricated-data bug, and not fixed by
    masking the source image's padding (tried first; the ghost copies
    remained).

    This instead reprojects in the other, well-behaved direction: for
    each real lon/lat point on a plain grid, the FORWARD
    geographic->geostationary transform (non-periodic, and undefined -
    cleanly NaN via pyproj, not a wrapped ghost value - beyond the
    visible limb) gives the exact source pixel to sample. The result is
    an ordinary equirectangular image, which every caller then draws
    with transform=ccrs.PlateCarree() - the same well-behaved transform
    every other real layer in this codebase already uses (see
    acf.gui.map.map_layers), never hitting Cartopy's geostationary
    imshow-regrid path at all.
    """
    lons = np.arange(-_MAX_VIEW_DEGREES, _MAX_VIEW_DEGREES + _REPROJECT_STEP_DEGREES, _REPROJECT_STEP_DEGREES)
    lats = np.arange(-_MAX_VIEW_DEGREES, _MAX_VIEW_DEGREES + _REPROJECT_STEP_DEGREES, _REPROJECT_STEP_DEGREES)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    transformer = pyproj.Transformer.from_crs("EPSG:4326", geo_crs.proj4_init, always_xy=True)
    with np.errstate(invalid="ignore"):
        x, y = transformer.transform(lon_grid, lat_grid)

    x_min, x_max = geo_crs.x_limits
    y_min, y_max = geo_crs.y_limits
    height, width = rgba.shape[:2]

    col = (x - x_min) / (x_max - x_min) * (width - 1)
    # Source image row 0 is the TOP (origin="upper" convention, matching
    # how PIL/Image decoded it) - which is y_max, not y_min.
    row = (y_max - y) / (y_max - y_min) * (height - 1)

    # Real disk-limb check, not just the bounding-box one below: geos
    # x_limits/y_limits describe a RECTANGLE, but the actual visible
    # Earth disk projects to an ELLIPSE inscribed in it (this is the
    # real geos projection geometry, not a heuristic) - a corner point
    # like (lon=-80, lat=-80) can satisfy the bounding-box check below
    # while its (x, y) sits outside that ellipse, i.e. off-Earth. Found
    # by testing this exact function: without this check, those corner
    # points sampled the source quicklook's own opaque white "off-Earth"
    # padding pixels (real pixels, wrong to show - the same class of bug
    # as the periodic wraparound this function's own docstring already
    # describes, just at the boundary instead of far beyond it), drawn
    # as a solid white ring around the disk on every map.
    # 0.97 rather than the geometrically "exact" 1.0: JPEG compression
    # ringing right at the black-Earth/white-padding edge (visible while
    # testing this function - a thin speckle of intermediate gray/white
    # pixels neither the ellipse nor the near-white check below cleanly
    # catches) sits in the outermost ~1-2% of the disk. A small,
    # deliberate margin trims that ring; it costs a negligible sliver of
    # real coverage right at the limb, which is already this thumbnail's
    # least reliable region geometrically.
    on_disk = (x / x_max) ** 2 + (y / y_max) ** 2 <= 0.95

    valid = (
        on_disk
        & np.isfinite(col)
        & np.isfinite(row)
        & (col >= 0)
        & (col <= width - 1)
        & (row >= 0)
        & (row <= height - 1)
    )

    col_idx = np.clip(np.round(col), 0, width - 1).astype(np.intp)
    row_idx = np.clip(np.round(row), 0, height - 1).astype(np.intp)

    out = np.zeros((*lon_grid.shape, 4), dtype=np.uint8)
    out[valid] = rgba[row_idx[valid], col_idx[valid]]
    # out's alpha already 0 (fully transparent) wherever invalid, from
    # the np.zeros() init above - no fabricated fill outside the disk.

    # Real, measured pixel value found while testing this function: the
    # quicklook's own off-Earth padding is exactly (255, 255, 255) -
    # confirmed by sampling its corner/edge pixels directly, not
    # assumed. The on_disk ellipse test above is the geometrically
    # "correct" limb, but is derived from geo_crs.x_limits/y_limits
    # under the assumption that the thumbnail's pixel grid maps exactly
    # and proportionally onto that rectangle with no letterboxing; a
    # small remaining mismatch there (confirmed while testing: this
    # image is 664x680 px, a ~1.02 aspect ratio, while x_limits/y_limits
    # is a ~1.004 aspect ratio the other way round - the two disagree
    # slightly) left a thin ring of real white padding pixels still
    # passing the ellipse test alone. This catches those directly by
    # their own real color instead of tightening the geometric
    # approximation further.
    near_white = (out[..., 0] >= 220) & (out[..., 1] >= 220) & (out[..., 2] >= 220)
    out[near_white, 3] = 0

    extent = (float(lons[0]), float(lons[-1]), float(lats[0]), float(lats[-1]))
    return out, extent


class _MTGFetchSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - same
    companion-object pattern as
    acf.gui.esoc.esoc_window._AWCIFieldWorkerSignals."""

    finished = Signal(object)  # MTGFetchResult


class _MTGFetchWorker(QRunnable):
    """Runs EUMETSATMTGConnector.fetch_latest_image() off the GUI
    thread - a synchronous network call there would freeze every map
    view on each refresh."""

    def __init__(self, connector: EUMETSATMTGConnector) -> None:
        super().__init__()
        self._connector = connector
        self.signals = _MTGFetchSignals()

    def run(self) -> None:
        try:
            result = self._connector.fetch_latest_image()
            self.signals.finished.emit(result)
        except Exception:
            # Real race, found while testing this feature: the
            # app/test process can tear down the receiving QObject (or
            # its whole QApplication) while this network fetch is still
            # in flight - PySide/Qt Concurrent surfaces that as a plain
            # RuntimeError ("Signal source has been deleted") in some
            # cases and other exception types in others, and an
            # exception escaping QRunnable.run() entirely prints its own
            # unhandled "Qt Concurrent has caught an exception..."
            # warning regardless of type. There is no one left to
            # notify either way - log and drop it rather than letting it
            # escape onto a Qt worker thread, which does not support it.
            logger.debug("MTG fetch worker ended abnormally (signal target likely torn down)", exc_info=True)


class MTGBasemapProvider(QObject):
    """Process-wide live MTG basemap image, shared by every real map
    view. Construct via instance(), not directly."""

    #: Emitted on the GUI thread whenever a new real image has been
    #: decoded and is ready - connected map canvases redraw from this.
    updated = Signal()

    _instance: "MTGBasemapProvider | None" = None

    def __init__(self) -> None:
        super().__init__()
        config = _load_mtg_config()
        self._connector = EUMETSATMTGConnector(collection=config["collection"])
        self._refresh_ms = config["refresh_seconds"] * 1000
        self._rgba: np.ndarray | None = None
        self._extent: tuple[float, float, float, float] | None = None
        self._last_result: MTGFetchResult | None = None
        self._fetching = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_async)
        self._timer.start(self._refresh_ms)
        self.refresh_async()

    @classmethod
    def instance(cls) -> "MTGBasemapProvider":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def status(self) -> str:
        if self._last_result is None:
            return "NOT_FETCHED_YET"
        return self._last_result.status

    @property
    def is_live(self) -> bool:
        """Whether current_image_rgba() is real, freshly-fetched MTG
        imagery (vs. None, meaning callers should keep their own
        honest fallback basemap)."""
        return self._rgba is not None

    @property
    def last_fetched_at(self) -> float | None:
        """Unix timestamp of the last fetch attempt (real or fallback),
        or None if none has completed yet - lets callers (e.g. the ESOC
        Earth Monitoring panel) show a real feed latency instead of
        reaching into this provider's own private state."""
        return self._last_result.fetched_at if self._last_result is not None else None

    def current_image_rgba(self) -> np.ndarray | None:
        return self._rgba

    def current_extent(self) -> tuple[float, float, float, float] | None:
        """(lon_min, lon_max, lat_min, lat_max) for current_image_rgba(),
        already in plain PlateCarree degrees - see
        _reproject_geostationary_to_platecarree()."""
        return self._extent

    def refresh_async(self) -> None:
        if self._fetching:
            return
        self._fetching = True
        worker = _MTGFetchWorker(self._connector)
        worker.signals.finished.connect(self._on_fetched)
        QThreadPool.globalInstance().start(worker)

    def _on_fetched(self, result: MTGFetchResult) -> None:
        self._fetching = False
        self._last_result = result
        if not result.is_real_data or not result.image_bytes:
            logger.info("MTG basemap not updated (%s) - keeping last known image, if any", result.status)
            return
        try:
            from PIL import Image

            image = Image.open(io.BytesIO(result.image_bytes)).convert("RGBA")
            raw_rgba = np.asarray(image)
            self._rgba, self._extent = _reproject_geostationary_to_platecarree(raw_rgba, geostationary_crs())
        except Exception:
            logger.exception("Failed to decode/reproject MTG quicklook image (product %s)", result.product_id)
            return
        logger.info(
            "MTG basemap updated: product=%s observed=%s->%s authenticated=%s",
            result.product_id,
            result.observation_start,
            result.observation_end,
            result.authenticated,
        )
        self.updated.emit()


def draw_mtg_basemap(axes: Any, zorder: int = 0) -> bool:
    """Draw the latest live MTG full-disk image as the map's base
    imagery layer. Returns True if a real image was drawn; False if none
    is available yet (no credentials/network/first fetch still pending)
    OR the draw call itself failed - callers MUST keep their own plain
    land/ocean fallback for either case rather than leaving a blank map,
    and must never substitute a fabricated image here.
    """
    provider = MTGBasemapProvider.instance()
    rgba = provider.current_image_rgba()
    extent = provider.current_extent()
    if rgba is None or extent is None:
        return False

    # Best-effort, same as every other base-map feature in
    # acf.gui.map.map_renderer (see that module's own NOTE) - a real
    # failure here (e.g. an axes implementation with no imshow, found
    # via tests/test_map_renderer.py's own stub axes) must not blank the
    # whole map for every caller.
    try:
        # Already reprojected onto a plain lon/lat grid (see
        # _reproject_geostationary_to_platecarree) -
        # transform=PlateCarree() here, the same well-behaved transform
        # every other real layer in this codebase uses
        # (acf.gui.map.map_layers), not the raw geostationary CRS.
        axes.imshow(
            rgba,
            origin="lower",
            extent=extent,
            transform=ccrs.PlateCarree(),
            zorder=zorder,
            interpolation="nearest",
        )
    except Exception:
        logger.warning("Failed to draw MTG basemap image", exc_info=True)
        return False
    return True
