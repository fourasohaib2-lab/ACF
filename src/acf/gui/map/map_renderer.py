"""MapRenderer responsible for scientific base map & layer visualization on Matplotlib Cartopy GeoAxes."""

from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature


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
        """
        if axes is None:
            return

        # 1. Base Canvas Face & Background
        axes.set_facecolor("#0a0f1d")

        # 2. Oceans
        try:
            axes.add_feature(
                cfeature.OCEAN,
                facecolor="#122c44",
                zorder=0,
            )
        except Exception:
            pass

        # 3. Land / Continents
        try:
            axes.add_feature(
                cfeature.LAND,
                facecolor="#1c472a",
                edgecolor="none",
                zorder=1,
            )
        except Exception:
            pass

        # 4. Lakes
        try:
            axes.add_feature(
                cfeature.LAKES,
                facecolor="#184a6b",
                edgecolor="none",
                zorder=2,
            )
        except Exception:
            pass

        # 5. Rivers
        try:
            axes.add_feature(
                cfeature.RIVERS,
                linewidth=0.4,
                edgecolor="#4a90e2",
                zorder=3,
            )
        except Exception:
            pass

        # 6. Country Borders
        try:
            axes.add_feature(
                cfeature.BORDERS,
                linewidth=0.5,
                edgecolor="#708090",
                linestyle=":",
                zorder=4,
            )
        except Exception:
            pass

        # 7. Coastlines
        try:
            axes.coastlines(
                resolution="110m",
                linewidth=0.9,
                color="#E0E0E0",
                zorder=5,
            )
        except Exception:
            pass

        # 8. Latitude / Longitude Gridlines
        try:
            grid = axes.gridlines(
                draw_labels=True,
                linewidth=0.4,
                color="#607D8B",
                alpha=0.6,
                linestyle="--",
                zorder=6,
            )
            grid.top_labels = False
            grid.right_labels = False
            grid.xlabel_style = {"size": 8, "color": "#B0BEC5"}
            grid.ylabel_style = {"size": 8, "color": "#B0BEC5"}
        except Exception:
            pass

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
                color="#81D4FA",
                weight="bold",
                pad=6,
            )
