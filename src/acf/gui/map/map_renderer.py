"""MapRenderer responsible for scientific base map & layer visualization on Matplotlib Cartopy GeoAxes."""

import logging
from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature

logger = logging.getLogger("acf.gui.map.map_renderer")


class MapRenderer:
    """Renders scientific base map elements (Oceans, Continents, Coastlines, Country Borders, Lat/Lon Grid)."""

    def __init__(self) -> None:
        self.initialized = True

    def render(
        self,
        axes: Any,
        projection: ccrs.CRS | None = None,
        layer_manager: Any | None = None,
        title: str | None = None,
        active_layers: list[str] | None = None,
    ) -> None:
        """Render complete scientific Earth map onto Matplotlib Cartopy GeoAxes.

        Args:
            axes: Matplotlib Cartopy GeoAxes subplot instance.
            projection: Active Cartopy CRS projection.
            layer_manager: LayerManager instance for rendering scientific layer overlays.
            title: Optional map header title text.
            active_layers: List of active layer names if layer_manager not supplied.

        NOTE (correction): every base-map feature below used to be
        wrapped in `except Exception: pass` with no logging at all -
        each of Cartopy's `add_feature()`/`coastlines()`/`gridlines()`
        calls can genuinely raise (e.g. no network route to download
        the real Natural Earth shapefile the first time a resolution
        is used, a corrupted local cache) and the map would silently
        render with that feature simply missing - no coastlines, no
        borders - with zero diagnostic trail for a user or developer to
        find out why. Each feature is still best-effort (one real
        failure must not blank the whole map), but the real exception
        is now logged, not discarded.
        """
        if axes is None:
            return

        # 1. Base Canvas Face & Background
        axes.set_facecolor("#0b1220")

        # 2. Oceans
        try:
            axes.add_feature(
                cfeature.OCEAN,
                facecolor="#121a2b",
                zorder=0,
            )
        except Exception:
            logger.warning("Failed to render ocean feature", exc_info=True)

        # 3. Land / Continents
        try:
            axes.add_feature(
                cfeature.LAND,
                facecolor="#1c472a",
                edgecolor="none",
                zorder=1,
            )
        except Exception:
            logger.warning("Failed to render land feature", exc_info=True)

        # 4. Lakes
        try:
            axes.add_feature(
                cfeature.LAKES,
                facecolor="#184a6b",
                edgecolor="none",
                zorder=2,
            )
        except Exception:
            logger.warning("Failed to render lakes feature", exc_info=True)

        # 5. Rivers
        try:
            axes.add_feature(
                cfeature.RIVERS,
                linewidth=0.4,
                edgecolor="#4a90e2",
                zorder=3,
            )
        except Exception:
            logger.warning("Failed to render rivers feature", exc_info=True)

        # 6. Country Borders
        try:
            axes.add_feature(
                cfeature.BORDERS,
                linewidth=0.5,
                edgecolor="#34445f",
                linestyle=":",
                zorder=4,
            )
        except Exception:
            logger.warning("Failed to render country borders feature", exc_info=True)

        # 7. Coastlines
        try:
            axes.coastlines(
                resolution="110m",
                linewidth=0.9,
                color="#e8edf5",
                zorder=5,
            )
        except Exception:
            logger.warning("Failed to render coastlines", exc_info=True)

        # 8. Latitude / Longitude Gridlines
        try:
            grid = axes.gridlines(
                draw_labels=True,
                linewidth=0.4,
                color="#6b7a94",
                alpha=0.6,
                linestyle="--",
                zorder=6,
            )
            grid.top_labels = False
            grid.right_labels = False
            grid.xlabel_style = {"size": 8, "color": "#9fb0c9"}
            grid.ylabel_style = {"size": 8, "color": "#9fb0c9"}
        except Exception:
            logger.warning("Failed to render lat/lon gridlines", exc_info=True)

        # 9. Render Scientific Layer Overlays
        if layer_manager is not None:
            if active_layers is not None:
                layer_manager.set_active_layers(active_layers)
            layer_manager.render_layers(axes, transform=ccrs.PlateCarree())

        # 10. Map Header Title & Metadata
        if title:
            axes.set_title(
                title,
                fontsize=10,
                color="#7ad4ff",
                weight="bold",
                pad=6,
            )
