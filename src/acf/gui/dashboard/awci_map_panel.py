"""
AWCI Map Panel
==============

Real Cartopy map (land/ocean/borders/coastline, PlateCarree projection) with
the AWCI complexity field drawn as a filled contour heatmap on top, plus an
optional flight path with labeled endpoints - matching the reference
mockup's global/regional map panels.

See awci_synthetic_field.py's own docstring for what is and is not real
here: the underlying meteorological inputs are a synthetic demo pattern,
but the AWCI score contoured on the map is the genuine AWCICalculator
output for those inputs, and the coastlines/borders are real Cartopy/
Natural Earth geography, not illustrative sketches.
"""

from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP
from acf.gui.dashboard.awci_synthetic_field import awci_grid


class AWCIMapPanel(QWidget):
    """A titled Cartopy map with the AWCI heatmap overlay."""

    def __init__(
        self,
        title: str = "AWCI GLOBAL MAP",
        extent: tuple[float, float, float, float] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Parameters
        ----------
        extent : (lon_min, lon_max, lat_min, lat_max) or None for global.
        """
        super().__init__(parent)
        self._title = title
        self._extent = extent
        self._flight_path: list[tuple[float, float, str]] = []  # (lat, lon, label)
        self._point_marker: tuple[float, float] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0d1b2a")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.axis = self.figure.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        self._contour = None
        self._flight_level_hpa = 300.0
        self._time_offset_hours = 0.0
        # When set (via set_external_field()), update_data() draws THIS
        # field instead of recomputing awci_grid()'s synthetic pattern -
        # lets a caller (AWCIDashboard's "Real Physics" mode) show a real
        # acf.awci.spatial_field.compute_real_complexity_field() result
        # on the exact same map widget, without a second implementation.
        self._external_field: tuple[list[float], list[float], Any] | None = None
        self._base_title = title

        self.update_data(flight_level_hpa=300.0)

    def set_flight_path(self, points: list[tuple[float, float, str]]) -> None:
        """points: list of (lat, lon, label), e.g. [(40.6, -73.8, 'JFK'), (49.0, 2.5, 'CDG')]."""
        self._flight_path = points
        self.update_data(self._flight_level_hpa, self._time_offset_hours)

    def set_point_marker(self, lat: float, lon: float) -> None:
        self._point_marker = (lat, lon)
        self.update_data(self._flight_level_hpa, self._time_offset_hours)

    def set_external_field(self, lons: list[float], lats: list[float], grid: Any, label: str) -> None:
        """
        Show a field this panel did not compute itself - e.g. a real
        acf.awci.spatial_field.compute_real_complexity_field() result -
        instead of the synthetic demo pattern. `label` is shown in the
        panel title (e.g. "REAL PHYSICS") so it's never ambiguous which
        kind of field is on screen. Redraws immediately.
        """
        self._external_field = (lons, lats, grid)
        self._title = f"{self._base_title} — {label}"
        self.update_data(self._flight_level_hpa, self._time_offset_hours)

    def clear_external_field(self) -> None:
        """Revert to the synthetic demo pattern (awci_grid())."""
        self._external_field = None
        self._title = self._base_title
        self.update_data(self._flight_level_hpa, self._time_offset_hours)

    def update_data(self, flight_level_hpa: float = 300.0, time_offset_hours: float = 0.0) -> None:
        """(Re)compute the AWCI grid and redraw the map. Uses the real
        AWCICalculator with synthetic demo inputs (see
        awci_synthetic_field.py) unless set_external_field() supplied a
        field to show instead."""
        self._flight_level_hpa = flight_level_hpa
        self._time_offset_hours = time_offset_hours
        self.axis.clear()

        if self._extent is not None:
            self.axis.set_extent(self._extent, crs=ccrs.PlateCarree())
            lon_range = (self._extent[0], self._extent[1])
            lat_range = (self._extent[2], self._extent[3])
            step = 1.5
        else:
            self.axis.set_global()
            lon_range = (-180.0, 180.0)
            lat_range = (-85.0, 85.0)
            step = 4.0

        self.axis.add_feature(cfeature.OCEAN, facecolor="#0a1929")
        self.axis.add_feature(cfeature.LAND, facecolor="#16213e")
        self.axis.add_feature(cfeature.COASTLINE, edgecolor="#4a5a7a", linewidth=0.5)
        self.axis.add_feature(cfeature.BORDERS, edgecolor="#3a4a6a", linewidth=0.3)

        if self._external_field is not None:
            lons, lats, grid = self._external_field
        else:
            lons, lats, grid = awci_grid(
                lat_step=step,
                lon_step=step,
                flight_level_hpa=flight_level_hpa,
                lat_range=lat_range,
                lon_range=lon_range,
                time_offset_hours=time_offset_hours,
            )
        self._contour = self.axis.contourf(
            lons, lats, grid, levels=20, cmap=AWCI_CMAP, vmin=0, vmax=100, alpha=0.75, transform=ccrs.PlateCarree()
        )

        for lat, lon, label in self._flight_path:
            self.axis.plot(lon, lat, marker="^", color="white", markersize=8, transform=ccrs.PlateCarree())
            self.axis.text(
                lon, lat - 3, label, color="white", fontsize=8, fontweight="bold",
                ha="center", transform=ccrs.PlateCarree(),
            )
        if len(self._flight_path) >= 2:
            path_lons = [p[1] for p in self._flight_path]
            path_lats = [p[0] for p in self._flight_path]
            self.axis.plot(
                path_lons, path_lats, linestyle="--", color="white", linewidth=1.3, transform=ccrs.PlateCarree()
            )

        if self._point_marker is not None:
            lat, lon = self._point_marker
            self.axis.plot(
                lon, lat, marker="o", color="white", markersize=6,
                markeredgecolor="black", transform=ccrs.PlateCarree(),
            )

        self.axis.set_title(self._title, color="#e0e0e0", fontsize=11, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.02)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"figure": self.figure is not None, "axis": self.axis is not None, "has_contour": self._contour is not None}
