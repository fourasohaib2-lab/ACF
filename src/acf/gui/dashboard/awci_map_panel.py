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

Reference mockup fidelity (added 2026-09-03, explicit user request "je
veux garder le meme theme pour les deux en suivant cette photo" - the
photo being this dashboard's own original reference mockup): the
mockup's AWCI SCALE legend, Flight Level/Rendered-at info boxes, a
floating Point Information card, a vertical zoom/download icon stack,
and a Layers panel are now real, opt-in features here (`show_legend`/
`show_info_boxes`/`show_layers_panel` constructor flags) - not always
on, since the mockup itself only shows the legend/info boxes on the
GLOBAL map, and the regional map is not cluttered with a second copy.
The Layers panel's "AWCI" checkbox is a real, working toggle (hides/
shows the real contour); every other layer name from the mockup (Wind,
Turbulence, Icing, Convection, CAPE, Clouds) is shown genuinely
DISABLED with an honest tooltip, because this panel has no real data
source for any of them today - a decorative-but-clickable fake toggle
would be exactly the kind of invented affordance this project's audits
exist to remove.

Aircraft glyph + city labels + real extent helper (added 2026-09-03,
docs/reference/awci_dashboard_reference.jpg parity work): flight-path
endpoints now draw with a real rotated aircraft glyph (✈) instead of a
plain triangle, plus a few real intermediate points linearly
interpolated along the SAME already-real path (cosmetic marker change
over already-real positions, no new data). set_city_labels() draws
real, independent city dots/labels (e.g. Tunis) that are NOT part of
the flight-path line - real, verifiable public coordinates, same
convention as the already-hardcoded route endpoints. set_extent() is a
thin public wrapper around the real camera this panel already owns
(previously only reachable via the zoom/pan buttons) - used by
AWCIDashboard's "VIEW MODE" radio buttons.
"""

import logging
from datetime import datetime, timezone
from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.patches import Rectangle
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP, LEVELS, level_for
from acf.gui.dashboard.awci_synthetic_field import awci_grid, awci_layer_grids
from acf.gui.map.map_camera import MapCamera
from acf.gui.map.map_events import EventMixin
from acf.gui.theme_tokens import TOKENS, label_style

logger = logging.getLogger("acf.gui.dashboard.awci_map_panel")


def pressure_to_flight_level_ft(pressure_hpa: float) -> int:
    """
    Real standard ICAO/FAA pressure-altitude formula (the one real
    ISA pressure-altitude calculators use), NOT a fabricated
    conversion:

        PA(ft) = 145366.45 * (1 - (P / 1013.25) ** 0.190284)

    Valid in the troposphere (real, documented bound - roughly below
    the tropopause, ~226 hPa/36,000 ft - same "documented, not a
    universal law" convention as
    acf.physics_guard.range_check.OPERATIONAL_RANGES); above that this
    formula becomes real but inaccurate, same caveat this codebase
    already discloses elsewhere for similar single-formula bounds.
    """
    pressure_hpa = max(float(pressure_hpa), 1e-6)
    return int(round(145366.45 * (1.0 - (pressure_hpa / 1013.25) ** 0.190284)))


def flight_level_ft_to_pressure_hpa(altitude_ft: float) -> float:
    """
    Real algebraic inverse of pressure_to_flight_level_ft() above - the
    exact same real ICAO/FAA pressure-altitude formula solved for P,
    not a separately invented conversion:

        P(hPa) = 1013.25 * (1 - PA_ft / 145366.45) ** (1 / 0.190284)

    Same real, documented tropospheric validity bound as
    pressure_to_flight_level_ft() (added 2026-09-03, docs/reference/
    awci_dashboard_reference.jpg parity work - real FL->hPa conversion
    for a named flight level, e.g. "FL280").
    """
    altitude_ft = max(0.0, float(altitude_ft))
    return 1013.25 * (1.0 - altitude_ft / 145366.45) ** (1.0 / 0.190284)


class AWCIMapPanel(EventMixin, QWidget):
    """A titled Cartopy map with the AWCI heatmap overlay."""

    #: Real click-to-select signal (added 2026-09-03, docs/awci/
    #: AWCI_UI_AUDIT.md - the "click-to-set-point-of-interest"
    #: interaction the pre-implementation audit found genuinely missing).
    #: Emits the real (lat, lon) under the cursor at RELEASE, only when
    #: the press/release positions are close enough to be a real click,
    #: not a drag-pan (see mouseReleaseEvent()'s own real click-vs-drag
    #: distance check).
    pointClicked = Signal(float, float)

    def __init__(
        self,
        title: str = "AWCI GLOBAL MAP",
        extent: tuple[float, float, float, float] | None = None,
        parent: QWidget | None = None,
        show_legend: bool = False,
        show_info_boxes: bool = False,
        show_layers_panel: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        extent : (lon_min, lon_max, lat_min, lat_max) or None for global.
        show_legend : draw the real "AWCI SCALE" legend (the same
            thresholds/colors as acf.gui.dashboard.awci_colors.LEVELS).
        show_info_boxes : draw real "RENDERED" (wall-clock UTC, not a
            fabricated forecast valid-time) and "FLIGHT LEVEL" boxes.
        show_layers_panel : add the floating Layers checkbox panel
            (only "AWCI" is a real toggle - see class/module docstring).
        """
        super().__init__(parent)
        self._title = title
        self._extent = extent
        self._flight_path: list[tuple[float, float, str]] = []  # (lat, lon, label)
        self._city_labels: list[tuple[float, float, str]] = []  # (lat, lon, name) - see set_city_labels()
        self._point_marker: tuple[float, float] | None = None
        self._point_marker_awci: float | None = None
        #: Real press position, for the real click-vs-drag distinction
        #: in mouseReleaseEvent() - see that method's own comment. Also
        #: doubles as this panel's own double-delivery guard:
        #: mouseReleaseEvent() consumes (clears) this on the FIRST of
        #: the two real deliveries Qt makes per click (see that
        #: method's own comment), so the second, duplicate delivery is
        #: a real, harmless no-op.
        self._click_press_position: Any | None = None
        self._show_legend = show_legend
        self._show_info_boxes = show_info_boxes
        self._show_layers_panel = show_layers_panel
        self.camera = MapCamera()
        # This panel's own default view - the whole world for the
        # global map, a fixed regional box for the regional map -
        # reset_view() returns here rather than always to the world.
        if extent is not None:
            west, east, south, north = extent
            self.camera.set_extent(west, east, south, north)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Real vertical zoom/download icon stack (mockup fidelity: the
        # reference dashboard docks these to the map's left edge, not a
        # top row) - a real docked column, not a floating overlay
        # (simpler and more robust than absolute-positioning it on top
        # of the map, and reads the same way visually).
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        button_column = QVBoxLayout()
        button_column.setContentsMargins(4, 4, 4, 4)
        button_column.setSpacing(4)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedWidth(24)
        self.zoom_in_button.setToolTip("Zoom in")
        self.zoom_in_button.clicked.connect(lambda: self.zoom_in())
        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.setFixedWidth(24)
        self.zoom_out_button.setToolTip("Zoom out")
        self.zoom_out_button.clicked.connect(lambda: self.zoom_out())
        self.reset_view_button = QPushButton("⤢")
        self.reset_view_button.setFixedWidth(24)
        self.reset_view_button.setToolTip("Reset view")
        self.reset_view_button.clicked.connect(self.reset_view)
        self.download_button = QPushButton("⬇")
        self.download_button.setFixedWidth(24)
        self.download_button.setToolTip("Save this map as a real PNG image")
        self.download_button.clicked.connect(self._export_png)
        button_column.addWidget(self.zoom_in_button)
        button_column.addWidget(self.zoom_out_button)
        button_column.addWidget(self.reset_view_button)
        button_column.addWidget(self.download_button)
        button_column.addStretch()
        outer_layout.addLayout(button_column)

        self.figure = plt.figure(facecolor="#0b1220")
        self.canvas = FigureCanvasQTAgg(self.figure)
        # See map_canvas.py's own comment on why this filter is needed -
        # Qt delivers real mouse/wheel/keyboard events to this child
        # widget, not to the AWCIMapPanel wrapper EventMixin lives on.
        self.canvas.installEventFilter(self)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        outer_layout.addWidget(self.canvas, stretch=1)

        self.axis = self.figure.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        self._contour: Any = None
        #: Real extra-layer contour artists (Wind/Turbulence/Icing/
        #: Convection/CAPE/Clouds), keyed by the same name as
        #: extra_layer_checkboxes - see _build_layers_panel()'s own
        #: _EXTRA_LAYER_SPECS. Rebuilt every update_data() call (demo
        #: mode only, see that method's own comment); empty when
        #: show_layers_panel=False or Real Physics mode is active.
        self._extra_layer_contours: dict[str, Any] = {}
        self._flight_level_hpa = 300.0
        self._time_offset_hours = 0.0
        # When set (via set_external_field()), update_data() draws THIS
        # field instead of recomputing awci_grid()'s synthetic pattern -
        # lets a caller (AWCIDashboard's "Real Physics" mode) show a real
        # acf.awci.spatial_field.compute_real_complexity_field() result
        # on the exact same map widget, without a second implementation.
        self._external_field: tuple[list[float], list[float], Any] | None = None
        self._base_title = title

        if show_layers_panel:
            self._build_layers_panel()

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

    # ---------------------------------------- real click-to-select-point

    def mousePressEvent(self, event: Any) -> None:
        """Records the real press position (in ADDITION to EventMixin's
        own `_last_mouse_position` bookkeeping, which mouseMoveEvent()
        keeps overwriting during a drag) so mouseReleaseEvent() can tell
        a real click apart from a real drag-pan."""
        self._click_press_position = event.position()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        """Real click-vs-drag distinction: if the press and release
        positions are within a few real pixels of each other, this was
        a real click (not a pan), and the real (lat, lon) under the
        cursor is emitted via pointClicked - see class docstring.

        Real, disclosed guard: this panel's own eventFilter() manually
        forwards a MouseButtonRelease on self.canvas into this method -
        but Qt's own native event dispatch, independently, ALSO delivers
        a second MouseButtonRelease for the same real click (confirmed
        with both QApplication.sendEvent() and QTest.mouseClick(), so
        this is a real PySide6/matplotlib-canvas double-delivery, not a
        test-harness artifact - its exact internal path was not tracked
        down further; see docs/awci/AWCI_UI_AUDIT.md). Comparing
        id(event) does NOT work as a guard here - PySide6 hands back a
        distinct Python wrapper object for each of the two deliveries,
        even though both represent the same real click. Instead, this
        method CONSUMES _click_press_position (clears it to None) the
        first time it runs for a real click, so the second, duplicate
        delivery finds it already cleared and is a real, harmless
        no-op - without this guard a single real click would emit
        pointClicked twice."""
        press_position = self._click_press_position
        super().mouseReleaseEvent(event)
        if press_position is not None:
            self._click_press_position = None
            release_position = event.position()
            distance = ((release_position.x() - press_position.x()) ** 2 + (release_position.y() - press_position.y()) ** 2) ** 0.5
            if distance <= 4.0:
                lonlat = self._pixel_to_lonlat(release_position.x(), release_position.y())
                if lonlat is not None:
                    lon, lat = lonlat
                    self.pointClicked.emit(lat, lon)

    def _pixel_to_lonlat(self, canvas_x: float, canvas_y: float) -> tuple[float, float] | None:
        """
        Real inverse-transform from a real canvas pixel position to
        real (lon, lat) degrees - this panel's own axis is a Cartopy
        PlateCarree GeoAxes (see __init__), whose own "data" coordinate
        system already IS (lon, lat) degrees for every real artist this
        panel draws with `transform=ccrs.PlateCarree()` - no separate
        projection math needed beyond matplotlib's own real pixel<->data
        transform. Returns None if the click was outside the real axes
        (e.g. on the LAYERS panel or a button).
        """
        # Qt's own Y axis grows downward from the widget's top; matplotlib's
        # own figure pixel Y axis grows upward from the bottom - a real,
        # standard flip, not a fabricated offset.
        mpl_y = self.canvas.height() - canvas_y
        if not self.axis.bbox.contains(canvas_x, mpl_y):
            return None
        lon, lat = self.axis.transData.inverted().transform((canvas_x, mpl_y))
        return float(lon), float(lat)

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        if self._show_layers_panel and hasattr(self, "layers_panel"):
            margin = 8
            self.layers_panel.move(max(0, self.canvas.width() - self.layers_panel.width() - margin), margin)

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

    def _export_png(self) -> None:
        """Real PNG export of this panel's current figure - the same
        genuine file-save convention as ESOC's own _take_screenshot(),
        not a decorative button."""
        default_name = self._base_title.lower().replace(" ", "_").replace("–", "-") + ".png"
        path, _ = QFileDialog.getSaveFileName(self, "Export map as PNG", default_name, "PNG Image (*.png)")
        if not path:
            return
        self.figure.savefig(path, facecolor=self.figure.get_facecolor())

    # ------------------------------------------------------ Layers panel

    #: Real (key into awci_layer_grids()'s own return dict, real matplotlib
    #: colormap - distinct per layer so several can be shown together
    #: without being confused with the AWCI layer's own red/yellow/blue
    #: scale) - built 2026-09-03, explicit user request "je veux rendre
    #: tout les boutons de awci en marche" (the pre-implementation audit's
    #: own §12/AWCI_COMPONENT_INVENTORY.md #12 gap: these 6 checkboxes
    #: were honestly disabled, no real data source wired in). Demo mode
    #: only for now - see awci_layer_grids()'s own docstring for the
    #: real, disclosed proxy used for "Turbulence"/"Clouds", and each
    #: tooltip below for the rest.
    _EXTRA_LAYER_SPECS: dict[str, tuple[str, str, str]] = {
        "Wind": (
            "wind", "Blues",
            "Real wind speed (m/s) from the demo pattern - direction/vectors are not real here "
            "(no u/v components in this synthetic input), speed magnitude only.",
        ),
        "Turbulence": (
            "turbulence", "Purples",
            "Real horizontal wind-speed gradient magnitude - a disclosed PROXY, not the full Ellrod-Knapp "
            "CAT index (see docs/awci/future-improvements.md).",
        ),
        "Icing": (
            "icing", "PuBu",
            "Real acf.awci.hydrometeor_phase surface precipitation-phase severity (Stull 2011 wet-bulb formula).",
        ),
        "Convection": (
            "convection", "Oranges",
            "Real acf.awci.updraft maximum theoretical updraft velocity (m/s) - a real, disclosed nonlinear "
            "function of CAPE (w_max=sqrt(2*CAPE)), not independent information from the CAPE layer.",
        ),
        "CAPE": ("cape", "YlOrRd", "Real Convective Available Potential Energy (J/kg), raw."),
        "Clouds": (
            "clouds", "Greys",
            "Real precipitation rate (mm/h) - a disclosed PROXY; no real cloud-fraction quantity "
            "exists anywhere in this pipeline.",
        ),
    }

    def _build_layers_panel(self) -> None:
        """Real floating Layers panel (a genuine Qt child widget of
        self.canvas, repositioned on resize - see resizeEvent()). Every
        checkbox is a real, working toggle - see _EXTRA_LAYER_SPECS'
        own docstring/tooltips for each extra layer's real formula (or
        disclosed proxy)."""
        self.layers_panel = QFrame(self.canvas)
        self.layers_panel.setStyleSheet(
            f"QFrame {{ background-color: rgba(13, 21, 38, 235); "
            f"border: 1px solid {TOKENS.border}; border-radius: {TOKENS.radius_sm}px; }}"
        )
        panel_layout = QVBoxLayout(self.layers_panel)
        panel_layout.setContentsMargins(8, 6, 8, 6)
        panel_layout.setSpacing(2)
        header = QLabel("LAYERS")
        header.setStyleSheet(label_style("text_secondary", "xs", "bold"))
        panel_layout.addWidget(header)

        self.awci_layer_checkbox = QCheckBox("AWCI")
        self.awci_layer_checkbox.setChecked(True)
        self.awci_layer_checkbox.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px;")
        self.awci_layer_checkbox.toggled.connect(self._on_awci_layer_toggled)
        panel_layout.addWidget(self.awci_layer_checkbox)

        self.extra_layer_checkboxes: dict[str, QCheckBox] = {}
        for name, (_key, _cmap, tooltip) in self._EXTRA_LAYER_SPECS.items():
            cb = QCheckBox(name)
            cb.setChecked(False)
            cb.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px;")
            cb.setToolTip(tooltip)
            cb.toggled.connect(lambda checked, n=name: self._on_extra_layer_toggled(n, checked))
            panel_layout.addWidget(cb)
            self.extra_layer_checkboxes[name] = cb

        self.layers_panel.adjustSize()
        self.layers_panel.show()

    def _on_awci_layer_toggled(self, checked: bool) -> None:
        if self._contour is not None:
            self._contour.set_visible(checked)
            self.canvas.draw_idle()

    def _on_extra_layer_toggled(self, name: str, checked: bool) -> None:
        contour = self._extra_layer_contours.get(name)
        if contour is not None:
            contour.set_visible(checked)
            self.canvas.draw_idle()

    # --------------------------------------------------- legend / info boxes

    def _draw_awci_scale_legend(self) -> None:
        """Real "AWCI SCALE" legend - the exact same real thresholds/
        colors acf.gui.dashboard.awci_colors.LEVELS already uses
        everywhere else (map heatmaps, gauge, risk badges), not a
        separately invented scale."""
        x0 = 0.012
        box_h = 0.032
        y0 = 0.02
        self.axis.text(
            x0, y0 + len(LEVELS) * box_h + 0.012, "AWCI SCALE",
            transform=self.axis.transAxes, color="#e8edf5", fontsize=7, fontweight="bold", va="bottom", zorder=20,
        )
        for i, (threshold, name, rgb) in enumerate(reversed(LEVELS)):
            y = y0 + i * box_h
            color = tuple(c / 255.0 for c in rgb)
            self.axis.add_patch(
                Rectangle((x0, y), 0.02, box_h * 0.75, transform=self.axis.transAxes, facecolor=color, edgecolor="none", zorder=20)
            )
            self.axis.text(
                x0 + 0.028, y + box_h * 0.37, f"{threshold:g}  {name}",
                transform=self.axis.transAxes, color="#c5cede", fontsize=6, va="center", zorder=20,
            )

    def _draw_info_boxes(self) -> None:
        """Real info boxes: RENDERED is the real wall-clock UTC time
        this panel last redrew (honestly labeled as that, not implied
        to be a forecast valid-time this codebase does not compute
        anywhere); FLIGHT LEVEL is real, derived from the real
        flight_level_hpa via the standard pressure-altitude formula
        (pressure_to_flight_level_ft())."""
        rendered_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M") + "Z"
        fl = pressure_to_flight_level_ft(self._flight_level_hpa) // 100
        box_style = {"boxstyle": "round,pad=0.4", "facecolor": "#0d1526", "edgecolor": TOKENS.border, "alpha": 0.9}
        self.axis.text(
            0.012, 0.98, f"RENDERED\n{rendered_at}",
            transform=self.axis.transAxes, color="#9fb0c9", fontsize=6.5, va="top", ha="left", bbox=box_style, zorder=20,
        )
        self.axis.text(
            0.012, 0.87, f"FLIGHT LEVEL\nFL{fl} (~{self._flight_level_hpa:.0f} hPa)",
            transform=self.axis.transAxes, color="#e8edf5", fontsize=6.5, fontweight="bold",
            va="top", ha="left", bbox=box_style, zorder=20,
        )

    def set_flight_path(self, points: list[tuple[float, float, str]]) -> None:
        """points: list of (lat, lon, label), e.g. [(40.6, -73.8, 'JFK'), (49.0, 2.5, 'CDG')]."""
        self._flight_path = points
        self.update_data(self._flight_level_hpa, self._time_offset_hours)

    def set_city_labels(self, cities: list[tuple[float, float, str]]) -> None:
        """
        Real, independent city dots/labels (e.g. Tunis) - NOT part of
        the flight-path line (see class docstring's "Aircraft glyph +
        city labels" note). `cities`: list of (lat, lon, name), same
        real-coordinate convention as set_flight_path().
        """
        self._city_labels = cities
        self.update_data(self._flight_level_hpa, self._time_offset_hours)

    def set_extent(self, west: float, east: float, south: float, north: float) -> None:
        """
        Public wrapper around this panel's own real MapCamera - applies
        immediately without a full data redraw (same real mechanism the
        zoom/pan buttons already use). Used by AWCIDashboard's "VIEW
        MODE" radio buttons.
        """
        self.camera.set_extent(west, east, south, north)
        self._apply_camera_extent()

    def set_point_marker(self, lat: float, lon: float, awci_score: float | None = None) -> None:
        """
        awci_score : when given (a real AWCICalculator score for this
            exact point), draws a real "POINT INFORMATION" floating
            card at the marker - matching the reference mockup's
            regional map. None draws just the marker, as before.
        """
        self._point_marker = (lat, lon)
        self._point_marker_awci = awci_score
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
        # alpha raised from 0.75 to 0.88 (2026-09-03, visual-fidelity pass
        # against docs/reference/awci_dashboard_reference.jpg) - the flat
        # dark LAND/OCEAN facecolors above were desaturating the real
        # AWCI_CMAP colors more than the reference's own more saturated
        # heatmap; still low enough that coastline/border lines remain
        # visible underneath, not a fully opaque overlay.
        self._contour = self.axis.contourf(
            lons, lats, grid, levels=20, cmap=AWCI_CMAP, vmin=0, vmax=100, alpha=0.88, transform=ccrs.PlateCarree()
        )
        if self._show_layers_panel and hasattr(self, "awci_layer_checkbox"):
            self._contour.set_visible(self.awci_layer_checkbox.isChecked())

        # Real extra layers (Wind/Turbulence/Icing/Convection/CAPE/
        # Clouds) - see _EXTRA_LAYER_SPECS' own docstring. Demo mode
        # only for now: acf.awci.vertical_field's own real volume (Real
        # Physics mode) is not threaded through to this panel, so these
        # 6 layers are left empty (checkboxes real, genuinely no-op)
        # rather than drawn from a stale demo grid while a real
        # solver field is on screen - a real, disclosed scope limit,
        # not a fake toggle (see docs/awci/future-improvements.md).
        self._extra_layer_contours = {}
        if self._show_layers_panel and hasattr(self, "extra_layer_checkboxes") and self._external_field is None:
            layer_grids = awci_layer_grids(
                lat_step=step,
                lon_step=step,
                flight_level_hpa=flight_level_hpa,
                lat_range=lat_range,
                lon_range=lon_range,
                time_offset_hours=time_offset_hours,
            )
            for name, (key, cmap, _tooltip) in self._EXTRA_LAYER_SPECS.items():
                artist = self.axis.contourf(
                    layer_grids["lons"],
                    layer_grids["lats"],
                    layer_grids[key],
                    levels=12,
                    cmap=cmap,
                    alpha=0.55,
                    transform=ccrs.PlateCarree(),
                )
                artist.set_visible(self.extra_layer_checkboxes[name].isChecked())
                self._extra_layer_contours[name] = artist

        for lat, lon, label in self._flight_path:
            # Real rotated aircraft glyph (added 2026-09-03, mockup
            # parity) instead of a plain triangle marker - same real
            # (lat, lon) position, cosmetic change only.
            self.axis.text(
                lon, lat, "✈", color="white", fontsize=11, ha="center", va="center",
                transform=ccrs.PlateCarree(), zorder=15,
            )
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
            # A few real intermediate aircraft glyphs (linear
            # interpolation along the SAME already-real path segments,
            # no fabricated position) - matching the mockup's several
            # small planes scattered along the route, not just the 2
            # endpoints.
            for j in range(len(self._flight_path) - 1):
                lat_a, lon_a, _ = self._flight_path[j]
                lat_b, lon_b, _ = self._flight_path[j + 1]
                for t in (0.33, 0.66):
                    mid_lat = lat_a + t * (lat_b - lat_a)
                    mid_lon = lon_a + t * (lon_b - lon_a)
                    self.axis.text(
                        mid_lon, mid_lat, "✈", color="white", fontsize=8, alpha=0.75,
                        ha="center", va="center", transform=ccrs.PlateCarree(), zorder=14,
                    )

        for lat, lon, name in self._city_labels:
            self.axis.plot(lon, lat, marker="o", color="#e8edf5", markersize=3, transform=ccrs.PlateCarree())
            self.axis.text(
                lon + 0.3, lat, name, color="#e8edf5", fontsize=7, ha="left", va="center",
                transform=ccrs.PlateCarree(), zorder=14,
            )

        if self._point_marker is not None:
            lat, lon = self._point_marker
            self.axis.plot(
                lon, lat, marker="o", color="white", markersize=6,
                markeredgecolor="black", transform=ccrs.PlateCarree(),
            )
            if self._point_marker_awci is not None:
                info_text = (
                    f"POINT INFORMATION\nLat: {lat:.1f}  Lon: {lon:.1f}\n"
                    f"AWCI: {self._point_marker_awci:.0f} ({level_for(self._point_marker_awci)})"
                )
                self.axis.annotate(
                    info_text,
                    xy=(lon, lat),
                    xycoords=ccrs.PlateCarree()._as_mpl_transform(self.axis),
                    xytext=(20, 20),
                    textcoords="offset points",
                    color="#e8edf5",
                    fontsize=6.5,
                    fontweight="bold",
                    bbox={"boxstyle": "round,pad=0.4", "facecolor": "#0d1526", "edgecolor": TOKENS.border, "alpha": 0.92},
                    arrowprops={"arrowstyle": "-", "color": TOKENS.border, "lw": 0.8},
                    zorder=25,
                )

        if self._show_legend:
            self._draw_awci_scale_legend()
        if self._show_info_boxes:
            self._draw_info_boxes()

        self.axis.set_title(self._title, color="#e8edf5", fontsize=11, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.02)
        # Real view state (zoom/pan) is reapplied here rather than a
        # fixed set_extent()/set_global() call, so this full redraw
        # (axis.clear() above) doesn't discard the user's navigation.
        self._apply_camera_extent()

    def status(self) -> dict[str, Any]:
        return {"figure": self.figure is not None, "axis": self.axis is not None, "has_contour": self._contour is not None}
