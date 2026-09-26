"""
Read-only relay to the public EUMETSAT EUMETView WMS for AWCI Web observation overlays.

Only allow-listed layers, EPSG:3857 bounding boxes of standard XYZ tiles (zoom 0-12), image sizes up
to 2048 px and times that GetCapabilities actually offers for the layer are forwarded; nothing else
reaches the upstream URL. The latest time of a layer comes from GetCapabilities (cached 5 min, kept
when a refresh fails) and is returned in X-AWCI-Observed-At, so the UI never shows an observation as
synchronous with a forecast step.

A slow or failing EUMETView must never delay the forecast served by the same process: upstream calls
time out after 5 s, at most `max_concurrent` run at once (further requests fail at once with "busy"),
and a layer whose GetMap failed is answered "recently failed" for 60 s without contacting upstream.
Tiles are cached on disk per normalised request for 24 h, at most `max_files` files (oldest evicted).
Imagery © EUMETSAT.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Protocol

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response

UPSTREAM = "https://view.eumetsat.int/geoserver/wms"
ATTRIBUTION = "© EUMETSAT"
MERCATOR_MAX = 20037508.342789244
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"
CAPABILITIES_TTL_S = 300.0
FAILURE_TTL_S = 60.0
TILE_CACHE_TTL_S = 86400.0
MAX_TILE_ZOOM = 12
_NS = "{http://www.opengis.net/wms}"
_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?Z$")
_PERIOD_RE = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")

WMS_LAYERS: dict[str, dict[str, Any]] = {
    "mtg_fd:ir105_hrfi": {"label": "MTG FCI IR 10,5 µm", "group": "satellite"},
    "mtg_fd:rgb_geocolour": {"label": "MTG GeoColour", "group": "satellite"},
    "mtg_fd:rgb_dust": {"label": "MTG Dust RGB", "group": "satellite"},
    "mtg_fd:rgb_fog": {"label": "MTG Fog RGB", "group": "satellite"},
    "mtg_fd:rgb_cloudtype": {"label": "MTG Cloud Type RGB", "group": "clouds"},
    "mtg_fd:rgb_cloudphase": {"label": "MTG Cloud Phase RGB", "group": "clouds"},
    "msg_fes:cth": {"label": "MSG hauteur du sommet des nuages", "group": "clouds"},
    "msg_fes:clm": {"label": "MSG masque nuageux", "group": "clouds"},
    "msg_fes:rgb_convection": {"label": "MSG Convection RGB", "group": "convection"},
    "msg_fes:rdt": {"label": "MSG orages à développement rapide (RDT)", "group": "convection"},
    "mtg_fd:li_afa": {"label": "MTG LI aire des éclairs cumulée", "group": "convection"},
    "msg_fes:rgb_ash": {"label": "MSG Ash RGB (cendres)", "group": "ash"},
}


class WmsUpstreamError(RuntimeError):
    """EUMETView did not return a usable answer."""


class WmsFetcher(Protocol):
    def get(self, url: str, timeout: float) -> tuple[str, bytes]: ...


class UrllibWmsFetcher:
    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.headers.get_content_type(), response.read()


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _period(text: str) -> timedelta:
    """ISO-8601 duration in days, hours, minutes and seconds (the forms WMS 1.3 time dimensions use)."""
    match = _PERIOD_RE.match(text)
    if not match or not any(match.groups()):
        raise ValueError(f"unsupported WMS time period {text!r}")
    d, h, m, s = (int(g or 0) for g in match.groups())
    step = timedelta(days=d, hours=h, minutes=m, seconds=s)
    if step <= timedelta(0):
        raise ValueError(f"unsupported WMS time period {text!r}")
    return step


def _parts(text: str) -> list[tuple[datetime, datetime, timedelta | None]]:
    """(start, end, period) of every comma-separated part; an instant has start == end and no period."""
    out: list[tuple[datetime, datetime, timedelta | None]] = []
    for part in (p.strip() for p in text.split(",")):
        if "/" in part:
            start, end, period = part.split("/")
            out.append((_iso(start), _iso(end), _period(period)))
        elif part:
            out.append((_iso(part), _iso(part), None))
    return out


def parse_time_dimension(text: str, count: int) -> list[datetime]:
    """Latest `count` instants of a WMS 1.3 time dimension ("start/end/period" intervals and/or instants).

    Each interval is walked back from its own end with its own budget of `count` instants, so an old
    interval listed first can never hide the newest ones. Raises ValueError on an unsupported format.
    """
    found: set[datetime] = set()
    for first, t, step in _parts(text):
        taken = 0
        while t >= first and taken < count:
            found.add(t)
            taken += 1
            if step is None:
                break
            t -= step
    return sorted(found)[-count:]


def time_in_dimension(text: str, when: datetime) -> bool:
    """True when `when` is one of the instants the dimension offers (on an interval's period grid)."""
    for start, end, step in _parts(text):
        if start <= when <= end and (step is None and when == start or step is not None and (when - start) % step
                                     == timedelta(0)):
            return True
    return False


def tile_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    """EPSG:3857 bounds (minx, miny, maxx, maxy) of XYZ tile z/x/y (y counted from the north)."""
    size = 2 * MERCATOR_MAX / 2**z
    minx = -MERCATOR_MAX + x * size
    maxy = MERCATOR_MAX - y * size
    return minx, maxy - size, minx + size, maxy


def on_tile_grid(bbox: tuple[float, float, float, float]) -> bool:
    """True when `bbox` is (to 1 mm) the bounds of one XYZ tile of zoom 0..MAX_TILE_ZOOM."""
    width = bbox[2] - bbox[0]
    for z in range(MAX_TILE_ZOOM + 1):
        size = 2 * MERCATOR_MAX / 2**z
        if abs(width - size) > 1e-3:
            continue
        x, y = round((bbox[0] + MERCATOR_MAX) / size), round((MERCATOR_MAX - bbox[3]) / size)
        expected = tile_bbox(z, x, y)
        return 0 <= x < 2**z and 0 <= y < 2**z and all(abs(a - b) <= 1e-3 for a, b in zip(bbox, expected))
    return False


def capabilities_time_dimensions(xml: bytes) -> dict[str, str]:
    root = ET.fromstring(xml)
    out: dict[str, str] = {}
    for layer in root.iter(f"{_NS}Layer"):
        name = layer.findtext(f"{_NS}Name")
        dim = next((d for d in layer.findall(f"{_NS}Dimension") if d.get("name") == "time"), None)
        if name and dim is not None and dim.text:
            out[name] = dim.text.strip()
    return out


def _fmt(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class WmsTimeNotOffered(ValueError):
    """The requested time is not one the layer offers upstream."""


class WmsRelay:
    def __init__(self, fetcher: WmsFetcher, cache_dir: Path, timeout_s: float = 5.0,
                 clock: Callable[[], float] = time.monotonic, max_concurrent: int = 4,
                 queue_wait_s: float = 0.5, max_files: int = 5000) -> None:
        self.fetcher, self.cache_dir, self.timeout_s, self.clock = fetcher, Path(cache_dir), timeout_s, clock
        self.queue_wait_s, self.max_files = queue_wait_s, max_files
        self._slots = threading.BoundedSemaphore(max_concurrent)
        self._caps: tuple[float, dict[str, str]] | None = None
        self._caps_lock = threading.Lock()
        self._failed: dict[str, float] = {}

    def _fetch(self, url: str) -> tuple[str, bytes]:
        if not self._slots.acquire(timeout=self.queue_wait_s):
            raise WmsUpstreamError("EUMETView relay busy: too many upstream requests in flight")
        try:
            return self.fetcher.get(url, self.timeout_s)
        except OSError as exc:  # includes socket timeouts and URLError
            raise WmsUpstreamError(f"EUMETView request failed: {exc}") from exc
        finally:
            self._slots.release()

    def _dimensions(self) -> dict[str, str]:
        with self._caps_lock:  # one refresh at a time; others reuse its result
            if self._caps is None or self.clock() - self._caps[0] > CAPABILITIES_TTL_S:
                url = f"{UPSTREAM}?service=WMS&version=1.3.0&request=GetCapabilities"
                try:
                    _, body = self._fetch(url)
                    self._caps = (self.clock(), capabilities_time_dimensions(body))
                except (WmsUpstreamError, ET.ParseError) as exc:
                    if self._caps is None:
                        raise WmsUpstreamError(f"EUMETView capabilities unavailable: {exc}") from exc
                    # keep serving the previous capabilities; retry at the next TTL expiry
                    self._caps = (self.clock(), self._caps[1])
            return self._caps[1]

    def _dimension(self, layer: str) -> str:
        dim = self._dimensions().get(layer)
        if dim is None:
            raise WmsUpstreamError(f"layer {layer} has no time dimension upstream")
        return dim

    def times(self, layer: str, count: int) -> list[str]:
        try:
            return [_fmt(t) for t in parse_time_dimension(self._dimension(layer), count)]
        except ValueError as exc:
            raise WmsUpstreamError(f"EUMETView time dimension of {layer} not understood: {exc}") from exc

    def _evict(self) -> None:
        """Drop expired tiles, then the oldest ones beyond `max_files`."""
        files = sorted(((f.stat().st_mtime, f) for f in self.cache_dir.glob("*.png")), key=lambda e: e[0])
        limit = time.time() - TILE_CACHE_TTL_S
        keep = [e for e in files if e[0] >= limit]
        for _, f in [e for e in files if e[0] < limit] + keep[: max(0, len(keep) - self.max_files)]:
            f.unlink(missing_ok=True)

    def tile(self, layer: str, when: str | None, bbox: tuple[float, float, float, float], width: int,
             height: int) -> tuple[bytes, str]:
        failed_at = self._failed.get(layer)
        if failed_at is not None and self.clock() - failed_at < FAILURE_TTL_S:
            raise WmsUpstreamError(f"EUMETView {layer} recently failed; retry after {FAILURE_TTL_S:.0f} s")
        if when is None:
            observed = self.times(layer, 1)[-1]
        else:
            try:
                offered = time_in_dimension(self._dimension(layer), _iso(when))
            except ValueError as exc:
                raise WmsUpstreamError(f"EUMETView time dimension of {layer} not understood: {exc}") from exc
            if not offered:
                raise WmsTimeNotOffered(f"{when} is not a time EUMETView offers for {layer}")
            observed = _fmt(_iso(when))
        params = {"service": "WMS", "version": "1.3.0", "request": "GetMap", "layers": layer, "styles": "",
                  "crs": "EPSG:3857", "bbox": ",".join(f"{v:.3f}" for v in bbox), "width": str(width),
                  "height": str(height), "format": "image/png", "transparent": "true", "time": observed}
        query = urllib.parse.urlencode(params)
        path = self.cache_dir / f"{hashlib.sha256(query.encode()).hexdigest()}.png"
        try:
            if time.time() - path.stat().st_mtime < TILE_CACHE_TTL_S:
                return path.read_bytes(), observed
        except FileNotFoundError:
            pass
        try:
            content_type, body = self._fetch(f"{UPSTREAM}?{query}")
            if content_type != "image/png":
                raise WmsUpstreamError(f"EUMETView answered {content_type} instead of a PNG")
        except WmsUpstreamError as exc:
            if "busy" not in str(exc):  # our own back-pressure says nothing about the upstream
                self._failed[layer] = self.clock()
            raise
        self._failed.pop(layer, None)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.cache_dir, suffix=".tmp")  # unique: concurrent writers never collide
        with os.fdopen(fd, "wb") as out:
            out.write(body)
        os.replace(tmp, path)
        self._evict()
        return body, observed


router = APIRouter()


def _relay(request: Request) -> WmsRelay:
    return request.app.state.awci_wms


def _layer(name: str) -> str:
    if name not in WMS_LAYERS:
        raise HTTPException(400, f"layer {name!r} is not relayed")
    return name


def _bbox(text: str) -> tuple[float, float, float, float]:
    try:
        values = tuple(float(v) for v in text.split(","))
    except ValueError as exc:
        raise HTTPException(400, "bbox must be 4 numbers") from exc
    if len(values) != 4 or not all(abs(v) <= MERCATOR_MAX for v in values) or values[0] >= values[2] \
            or values[1] >= values[3]:
        raise HTTPException(400, "bbox must be minx,miny,maxx,maxy inside the EPSG:3857 extent")
    bbox = values[0], values[1], values[2], values[3]
    if not on_tile_grid(bbox):
        raise HTTPException(400, f"bbox must be one XYZ tile of zoom 0-{MAX_TILE_ZOOM}")
    return bbox


@router.get("/wms/layers")
def wms_layers() -> list[dict[str, Any]]:
    return [{"layer": name, **meta, "attribution": ATTRIBUTION} for name, meta in WMS_LAYERS.items()]


@router.get("/wms/times")
def wms_times(request: Request, layer: str, count: Annotated[int, Query(ge=1, le=48)] = 1) -> dict[str, Any]:
    try:
        times = _relay(request).times(_layer(layer), count)
    except WmsUpstreamError as exc:
        raise HTTPException(502, str(exc)) from exc
    return {"layer": layer, "label": WMS_LAYERS[layer]["label"], "times": times, "attribution": ATTRIBUTION}


@router.get("/wms", response_model=None)
def wms_tile(request: Request, layer: str, bbox: str, width: Annotated[int, Query(ge=1, le=2048)] = 256,
             height: Annotated[int, Query(ge=1, le=2048)] = 256, time: str | None = None) -> Response:
    if time is not None and not _TIME_RE.match(time):
        raise HTTPException(400, "time must be ISO-8601 UTC, e.g. 2026-09-25T18:50:00Z")
    try:
        body, observed = _relay(request).tile(_layer(layer), time, _bbox(bbox), width, height)
    except WmsTimeNotOffered as exc:
        raise HTTPException(400, str(exc)) from exc
    except WmsUpstreamError as exc:
        raise HTTPException(502, str(exc)) from exc
    return Response(content=body, media_type="image/png", headers={
        "X-AWCI-Observed-At": observed, "X-AWCI-Attribution": "EUMETSAT",  # HTTP headers stay ASCII
        "Cache-Control": "public, max-age=86400" if time else "public, max-age=300"})
