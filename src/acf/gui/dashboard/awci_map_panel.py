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

Real zoom/pan (added 2026-09-02, explicit user request "ajoute
l'option zoom des cartes et manipulation totale des cartes"): same
EventMixin + MapCamera wiring as acf.gui.map.map_canvas.MapCanvas (see
that module's own docstring for the full rationale, including the
Mercator-singularity bug found and fixed there - not applicable here
since this panel uses PlateCarree, but the event-filter-on-the-child-
canvas lesson from that same work applies identically and is reused).
update_data() used to call self.axis.set_extent()/set_global()
directly on every redraw (including on every time_slider move), which
would have silently reset any zoom/pan the user had made; it now
applies the camera's current view via _apply_camera_extent() instead,
so panel data can refresh without discarding user navigation.
"""

import logging
from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP
from acf.gui.dashboard.awci_synthetic_field import awci_grid
from acf.gui.map.map_camera import MapCamera
from acf.gui.map.map_events import EventMixin

logger = logging.getLogger("acf.gui.dashboard.awci_map_panel")


class AWCIMapPanel(EventMixin, QWidget):
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
        self.camera = MapCamera()
        # This panel's own default view - the whole world for the
        # global map, a fixed regional box for the regional map -
        # reset_view() returns here rather than always to the world.
        if extent is not None:
            west, east, south, north = extent
            self.camera.set_extent(west, east, south, north)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(4, 2, 4, 2)
        controls_row.addStretch()
        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.setFixedWidth(24)
        self.zoom_out_button.setToolTip("Zoom out")
        self.zoom_out_button.clicked.connect(lambda: self.zoom_out())
        self.reset_view_button = QPushButton("⤢")
        self.reset_view_button.setFixedWidth(24)
        self.reset_view_button.setToolTip("Reset view")
        self.reset_view_button.clicked.connect(self.reset_view)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedWidth(24)
        self.zoom_in_button.setToolTip("Zoom in")
        self.zoom_in_button.clicked.connect(lambda: self.zoom_in())
        controls_row.addWidget(self.zoom_out_button)
        controls_row.addWidget(self.reset_view_button)
        controls_row.addWidget(self.zoom_in_button)
        layout.addLayout(controls_row)

        self.figure = plt.figure(facecolor="#0b1220")
        self.canvas = FigureCanvasQTAgg(self.figure)
        # See map_canvas.py's own comment on why this filter is needed -
        # Qt delivers real mouse/wheel/keyboard events to this child
        # widget, not to the AWCIMapPanel wrapper EventMixin lives on.
        self.canvas.installEventFilter(self)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
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

    def eventFilter(self, obj: Any, event: Any) -> bool:
        """See map_canvas.py's identical eventFilter() for the full
        rationale - forwards real input on self.canvas into EventMixin's
        handlers on this wrapper."""
        if obj is self.canvas:
            event_type = event.type()
            if event_type == QEvent.Type.Wheel:
                self.wheelEvent(event)
                return True
            if event_type == QEvent.Type.MouseButtonPress:
                self.mousePressEvent(event)
                return True
            if event_type == QEvent.Type.MouseMove:
                self.mouseMoveEvent(event)
                return True
            if event_type == QEvent.Type.MouseButtonRelease:
                self.mouseReleaseEvent(event)
                return True
            if event_type == QEvent.Type.MouseButtonDblClick:
                self.mouseDoubleClickEvent(event)
                return True
            if event_type == QEvent.Type.KeyPress:
                self.keyPressEvent(event)
                return True
        return super().eventFilter(obj, event)

    # -------------------------------------------------- zoom / pan / reset

    def zoom_in(self, factor: float = 1.2) -> None:
        self.camera.zoom_in(factor)
        self._apply_camera_extent()

    def zoom_out(self, factor: float = 1.2) -> None:
        self.camera.zoom_out(factor)
        self._apply_camera_extent()

    def reset_view(self) -> None:
        """Return to this panel's own default view (its configured
        `extent`, or the whole world for the global map) - not always
        the whole world."""
        if self._extent is not None:
            west, east, south, north = self._extent
            self.camera.set_extent(west, east, south, north)
        else:
            self.camera.reset()
        self._apply_camera_extent()

    def pan(self, dx: float, dy: float) -> None:
        zoom = max(self.camera.zoom_level, 1e-3)
        self.camera.pan(dx / zoom, dy / zoom)
        self._apply_camera_extent()

    def pan_left(self, step: float = 5.0) -> None:
        self.pan(-step, 0.0)

    def pan_right(self, step: float = 5.0) -> None:
        self.pan(step, 0.0)

    def pan_up(self, step: float = 5.0) -> None:
        self.pan(0.0, step)

    def pan_down(self, step: float = 5.0) -> None:
        self.pan(0.0, -step)

    def _apply_camera_extent(self) -> None:
        """Apply the camera's current view to the live axis and redraw,
        without rebuilding the whole map (update_data() is the heavier
        full-redraw path)."""
        west, east, south, north = self.camera.current_extent()
        try:
            self.axis.set_extent([west, east, south, north], crs=ccrs.PlateCarree())
        except Exception:
            logger.warning("AWCIMapPanel: failed to apply zoom/pan extent %s", self.camera.extent, exc_info=True)
            return
        self.canvas.draw_idle()

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

        # NOTE: the data range (lon_range/lat_range/step, used only to
        # bound the synthetic pattern's own grid below) stays tied to
        # this panel's configured extent/global default - it is NOT the
        # current zoomed/panned VIEW, which is applied separately at
        # the end via _apply_camera_extent() so a data refresh (e.g.
        # the time_slider) does not silently discard the user's zoom/pan.
        if self._extent is not None:
            lon_range = (self._extent[0], self._extent[1])
            lat_range = (self._extent[2], self._extent[3])
            step = 1.5
        else:
            lon_range = (-180.0, 180.0)
            lat_range = (-85.0, 85.0)
            step = 4.0

        self.axis.add_feature(cfeature.OCEAN, facecolor="#0f1830")
        self.axis.add_feature(cfeature.LAND, facecolor="#16213e")
        self.axis.add_feature(cfeature.COASTLINE, edgecolor="#34445f", linewidth=0.5)
        self.axis.add_feature(cfeature.BORDERS, edgecolor="#34445f", linewidth=0.3)

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

        self.axis.set_title(self._title, color="#e8edf5", fontsize=11, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.02)
        # Real view state (zoom/pan) is reapplied here rather than a
        # fixed set_extent()/set_global() call, so this full redraw
        # (axis.clear() above) doesn't discard the user's navigation.
        self._apply_camera_extent()

    def status(self) -> dict[str, Any]:
        return {"figure": self.figure is not None, "axis": self.axis is not None, "has_contour": self._contour is not None}
