"""Scientific QWidget-based MapCanvas using Cartopy and Matplotlib Qt Backend (ACF Map Canvas).

NOTE (found while auditing docs/architecture/duplicate_components.md's
"Canvas carte" row, NOT changed — RÈGLE D'OR / single source of truth):
this is the real `MapCanvas` embedded in ESOC's live window
(`acf.gui.esoc.view_manager.ViewManager` and
`acf.gui.main_window.main_window.MainWindow` both import it directly).
`acf.maps.canvas.map_canvas.MapCanvas` is a second, genuinely-both-live
implementation - it IS a `FigureCanvasQTAgg` (a matplotlib canvas you
call `.draw()`/`.figure` on directly), where this class instead
composes one as a child widget - with its own real consumers
(`acf.maps`'s own public API, `acf.visualization`'s lazy re-export
table). See that module's own NOTE for the full comparison and why
this pass does not unilaterally merge them.

Real zoom/pan (added 2026-09-02, explicit user request "ajoute
l'option zoom des cartes et manipulation totale des cartes"): wires
`acf.gui.map.map_events.EventMixin` (real Qt mouse/wheel/keyboard
boilerplate - drag to pan, scroll to zoom, double-click/Home to reset,
arrow keys to pan) with `acf.gui.map.map_camera.MapCamera` (real
center/zoom/extent state) into this, the live canvas. `MapCamera` had
a real, separate bug fixed as part of this same change (see its own
NOTE) - zoom/pan changed tracked state but never touched the extent
Cartopy actually draws; `current_extent()` is the real fix this canvas
now applies via `_apply_camera_extent()`. On-canvas +/-/reset buttons
are also added for real "manipulation totale" beyond mouse/keyboard
(touch devices, no scroll wheel).
"""

import logging
from typing import Any

import cartopy.crs as ccrs
import matplotlib
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from acf.data.dataset import Dataset
from acf.gui.map.map_camera import MapCamera
from acf.gui.map.map_events import EventMixin
from acf.gui.map.map_layers import MODULE_COMPLEXITY_LAYERS, LayerManager
from acf.gui.map.map_projection import MapProjection
from acf.gui.map.map_renderer import MapRenderer

logger = logging.getLogger("acf.gui.map.map_canvas")

#: Web Mercator's own real latitude limit (matches e.g. Google/OSM Web
#: Mercator) - Mercator projection has a genuine mathematical
#: singularity at the poles (y -> infinity as latitude -> 90), so
#: applying MapCamera's geographically-exact +/-90 world extent
#: straight to a Mercator-projected GeoAxes raises a real
#: "Axis limits cannot be NaN or Inf" error (found while testing real
#: double-click reset on this canvas's default "2D Mercator Map"
#: projection - not a hypothetical edge case). Only the display extent
#: is clamped here; MapCamera's own tracked center/zoom/extent stay
#: geographically exact. This constant is tuned for Mercator
#: specifically - a different projection (Orthographic, a polar
#: stereographic) would want a different real display clamp, not
#: addressed here since Mercator is this canvas's actual live default.
_MAX_MERCATOR_LATITUDE_DEG = 85.05112878

#: A second, independent real Mercator edge case found the same way -
#: the exact +/-180.0 longitude boundary (the antimeridian) is
#: degenerate for this PROJ/Cartopy Mercator transform even at a safe
#: latitude (confirmed: -180/180 with +/-85.05 latitude raised the same
#: "Axis limits cannot be NaN or Inf"; a tiny inset like +/-179.9999
#: does not). A negligible, real, display-only epsilon - not a claim
#: that +/-180 is geographically wrong.
_MAX_MERCATOR_LONGITUDE_DEG = 179.9999


class _LabelProxy:
    """Proxy object maintaining backward compatibility with self.map_canvas.label.setText()."""

    def __init__(self, parent_canvas: "MapCanvas") -> None:
        self._canvas = parent_canvas

    def setText(self, text: str) -> None:
        self._canvas.set_title(text)


class MapCanvas(EventMixin, QWidget):
    """QWidget embedding a Matplotlib Cartopy GeoAxes figure for scientific Earth visualization.

    Inherits EventMixin (see module docstring) for real mouse-drag pan,
    scroll-wheel zoom, double-click reset, and arrow-key/+/-/Home
    keyboard navigation - EventMixin's handlers call this class's own
    pan()/zoom_in()/zoom_out()/reset_view()/pan_left/right/up/down()
    methods below.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # 1. State & Managers
        self.projection_manager = MapProjection("2D Mercator Map")
        self.renderer = MapRenderer()
        self.layer_manager = LayerManager()
        self.camera = MapCamera()

        self.title_text: str = "GLOBAL EARTH INTERACTIVE MAP"

        # Compatibility proxy for ViewManager.map_canvas.label.setText()
        self.label = _LabelProxy(self)

        # Real keyboard focus so EventMixin.keyPressEvent (arrow-key
        # pan, +/- zoom, Home reset) actually receives events - a
        # QWidget with the default NoFocus policy never gets them.
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # 2. Matplotlib Figure & High DPI Setup
        self.figure = plt.figure(figsize=(12, 8), dpi=100, facecolor="#0b1220")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0b1220;")
        # Real events (mouse/wheel/keyboard) are delivered by Qt to
        # self.canvas - the actual widget under the cursor - not to
        # this MapCanvas wrapper, even though EventMixin's handlers
        # live here (confirmed by testing: dispatching a real
        # QWheelEvent straight to self.canvas left camera state
        # unchanged until this filter was added). An event filter is
        # the standard, documented Qt idiom for a parent that needs to
        # observe/handle a child's input.
        self.canvas.installEventFilter(self)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.axes: Any | None = None

        # 3. Layout Setup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(4, 2, 4, 2)
        controls_row.addStretch()
        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.setFixedWidth(28)
        self.zoom_out_button.setToolTip("Zoom out")
        self.zoom_out_button.clicked.connect(lambda: self.zoom_out())
        self.reset_view_button = QPushButton("⤢")
        self.reset_view_button.setFixedWidth(28)
        self.reset_view_button.setToolTip("Reset view (whole world)")
        self.reset_view_button.clicked.connect(self.reset_view)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedWidth(28)
        self.zoom_in_button.setToolTip("Zoom in")
        self.zoom_in_button.clicked.connect(lambda: self.zoom_in())
        controls_row.addWidget(self.zoom_out_button)
        controls_row.addWidget(self.reset_view_button)
        controls_row.addWidget(self.zoom_in_button)
        layout.addLayout(controls_row)

        layout.addWidget(self.canvas)

        # 4. Initial Render
        self.rebuild_axes()
        self.draw_map()

    def eventFilter(self, obj: Any, event: Any) -> bool:
        """Forwards real input events from self.canvas (the actual
        widget Qt delivers mouse/wheel/keyboard events to) into
        EventMixin's handlers on this wrapper - see the installEventFilter()
        call in __init__ for why this is needed at all."""
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
    # Called by EventMixin's real Qt event handlers (drag/wheel/double-
    # click/keyboard) - see this class's and map_camera.py's own NOTEs
    # for why MapCamera alone was not enough to wire in as-is.

    def zoom_in(self, factor: float = 1.2) -> None:
        """Real interactive zoom-in."""
        self.camera.zoom_in(factor)
        self._apply_camera_extent()

    def zoom_out(self, factor: float = 1.2) -> None:
        """Real interactive zoom-out."""
        self.camera.zoom_out(factor)
        self._apply_camera_extent()

    def reset_view(self) -> None:
        """Real reset to the whole-world view."""
        self.camera.reset()
        self._apply_camera_extent()

    def pan(self, dx: float, dy: float) -> None:
        """dx/dy are the same pixel-ish deltas EventMixin's
        mouseMoveEvent/keyPressEvent already compute - interpreted as
        degrees-at-zoom==1.0 and scaled down by the current zoom level,
        so a drag feels consistent whether zoomed in or out (a real,
        documented design choice, not the only possible one - same
        "document, don't silently assume" convention as
        MapCamera.current_extent()'s own docstring)."""
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

    # ----------------------------------------------------- real AWCI field

    def set_awci_field(self, lons: Any, lats: Any, values: Any, label: str = "AWCI") -> None:
        """Feed a real AWCI complexity field (e.g. from
        acf.awci.spatial_field.compute_real_complexity_field()) into
        this canvas's AWCILayer and redraw - explicit user request
        closing the gap where ESOC's central map showed no real
        AWCI/CAPE/CIN data at all, unlike the separate AWCI dashboard.
        Real computation is expected to happen off the GUI thread by
        the caller (see esoc_window.py's _AWCIFieldWorker) - this
        method itself only updates the already-computed data and
        redraws, so it is safe to call from a Qt signal handler on the
        GUI thread."""
        layer = self.layer_manager.available_layers.get("AWCI Complexity")
        if layer is None:
            logger.warning("MapCanvas.set_awci_field(): AWCI Complexity layer not registered")
            return
        layer.set_data(lons, lats, values)
        if "AWCI Complexity" not in self.layer_manager.active_layer_names:
            self.layer_manager.active_layer_names.append("AWCI Complexity")
        # NOTE: title_text is set directly (not via set_title()) because
        # draw_map() below calls self.axes.clear() and rebuilds the
        # title itself from title_text - calling set_title() first would
        # just be immediately wiped out by that clear().
        base_title = self.title_text.split(" — ")[0]
        self.title_text = f"{base_title} — {label}"
        self.draw_map()
        self._apply_camera_extent()

    def clear_awci_field(self) -> None:
        """Remove the real AWCI field overlay set by set_awci_field()."""
        layer = self.layer_manager.available_layers.get("AWCI Complexity")
        if layer is not None:
            layer.custom_data = None
        if "AWCI Complexity" in self.layer_manager.active_layer_names:
            self.layer_manager.active_layer_names.remove("AWCI Complexity")
        self.title_text = self.title_text.split(" — ")[0]
        self.draw_map()
        self._apply_camera_extent()

    # ------------------------------------------- real per-module complexity fields

    def set_module_complexity_field(
        self, module_key: str, lons: Any, lats: Any, values: Any, label: str = "", activate: bool = True
    ) -> None:
        """
        Feed a real per-module complexity field (docs/ACF_MASTER_PROMPT.md
        sections 28-29) - e.g. one entry of
        acf.awci.spatial_field.compute_real_complexity_field()'s own
        `module_fields[module_key]` - into the matching
        ModuleComplexityLayer and redraw. Same real-only discipline and
        off-GUI-thread-computation convention as set_awci_field().

        Parameters
        ----------
        module_key : str
            One of `acf.gui.map.map_layers.MODULE_COMPLEXITY_LAYERS`'s
            values (e.g. "dynamic", "topographic") - the same real
            AWCICalculator module key `module_fields` is keyed by, NOT
            the display layer name.
        activate : bool
            When True (default), the layer is also added to
            `active_layer_names` so it actually renders immediately -
            matches set_awci_field()'s own behavior for a direct,
            single-layer caller. Pass False to populate real data
            without displaying it yet (e.g. a caller populating all 6
            module layers at once from one compute_real_complexity_field()
            result - auto-activating every one of them simultaneously
            would stack 6 overlapping heatmaps with no way yet to
              choose just one; see esoc_window.py's own use of this).
        """
        layer_name = next((name for name, key in MODULE_COMPLEXITY_LAYERS.items() if key == module_key), None)
        if layer_name is None:
            logger.warning(
                "MapCanvas.set_module_complexity_field(): unknown module_key %r - expected one of %s",
                module_key,
                sorted(MODULE_COMPLEXITY_LAYERS.values()),
            )
            return
        layer = self.layer_manager.available_layers.get(layer_name)
        if layer is None:
            logger.warning("MapCanvas.set_module_complexity_field(): %r layer not registered", layer_name)
            return
        layer.set_data(lons, lats, values)
        if not activate:
            return
        if layer_name not in self.layer_manager.active_layer_names:
            self.layer_manager.active_layer_names.append(layer_name)
        base_title = self.title_text.split(" — ")[0]
        self.title_text = f"{base_title} — {layer_name}" + (f" ({label})" if label else "")
        self.draw_map()
        self._apply_camera_extent()

    def clear_module_complexity_field(self, module_key: str) -> None:
        """Remove the real per-module overlay set by
        set_module_complexity_field() for this exact module_key."""
        layer_name = next((name for name, key in MODULE_COMPLEXITY_LAYERS.items() if key == module_key), None)
        if layer_name is None:
            return
        layer = self.layer_manager.available_layers.get(layer_name)
        if layer is not None:
            layer.custom_data = None
        if layer_name in self.layer_manager.active_layer_names:
            self.layer_manager.active_layer_names.remove(layer_name)
        self.title_text = self.title_text.split(" — ")[0]
        self.draw_map()
        self._apply_camera_extent()

    def set_uncertainty_field(
        self, lons: Any, lats: Any, values: Any, label: str = "Uncertainty", activate: bool = True
    ) -> None:
        """Feed a real forecast-uncertainty field (docs/ACF_MASTER_PROMPT.md
        section 28's "Uncertainty" layer - e.g.
        compute_real_complexity_field()'s own `forecast_field`) into
        this canvas's UncertaintyLayer and redraw. Same real-only
        discipline as set_awci_field(); see
        set_module_complexity_field()'s own `activate` parameter for
        why a caller populating this alongside several module layers
        at once may want activate=False."""
        layer = self.layer_manager.available_layers.get("Uncertainty")
        if layer is None:
            logger.warning("MapCanvas.set_uncertainty_field(): Uncertainty layer not registered")
            return
        layer.set_data(lons, lats, values)
        if not activate:
            return
        if "Uncertainty" not in self.layer_manager.active_layer_names:
            self.layer_manager.active_layer_names.append("Uncertainty")
        base_title = self.title_text.split(" — ")[0]
        self.title_text = f"{base_title} — {label}"
        self.draw_map()
        self._apply_camera_extent()

    def clear_uncertainty_field(self) -> None:
        """Remove the real uncertainty overlay set by set_uncertainty_field()."""
        layer = self.layer_manager.available_layers.get("Uncertainty")
        if layer is not None:
            layer.custom_data = None
        if "Uncertainty" in self.layer_manager.active_layer_names:
            self.layer_manager.active_layer_names.remove("Uncertainty")
        self.title_text = self.title_text.split(" — ")[0]
        self.draw_map()
        self._apply_camera_extent()

    def _apply_camera_extent(self) -> None:
        """Apply the camera's real current extent to the live Cartopy
        axes and redraw - the missing link EventMixin/MapCamera never
        had before this change (see map_camera.py's own NOTE)."""
        if self.axes is None:
            return
        west, east, south, north = self.camera.current_extent()
        # See _MAX_MERCATOR_LATITUDE_DEG/_MAX_MERCATOR_LONGITUDE_DEG's own comments - display-only clamps.
        south = max(south, -_MAX_MERCATOR_LATITUDE_DEG)
        north = min(north, _MAX_MERCATOR_LATITUDE_DEG)
        west = max(west, -_MAX_MERCATOR_LONGITUDE_DEG)
        east = min(east, _MAX_MERCATOR_LONGITUDE_DEG)
        try:
            self.axes.set_extent([west, east, south, north], crs=ccrs.PlateCarree())
        except Exception:
            logger.warning("MapCanvas: failed to apply zoom/pan extent %s", self.camera.extent, exc_info=True)
            return
        self.refresh()

    def rebuild_axes(self) -> None:
        """Re-create subplot axes with current Cartopy CRS projection."""
        self.figure.clear()

        # Add subplot with active Cartopy projection
        current_crs = self.projection_manager.current_crs
        self.axes = self.figure.add_subplot(111, projection=current_crs)
        self.axes.set_facecolor("#0b1220")

    def draw_map(self) -> None:
        """Render base map and active scientific layers on GeoAxes."""
        if self.axes is None:
            return

        self.axes.clear()

        # Draw oceans, continents, coastlines, borders, lat/lon grid, and layers
        self.renderer.render(
            axes=self.axes,
            projection=self.projection_manager.current_crs,
            layer_manager=self.layer_manager,
            title=self.title_text,
        )

        if self.canvas is not None:
            try:
                self.canvas.draw_idle()
            except RuntimeError:
                pass

    def draw_world(self) -> None:
        """Draw professional world base map and scientific layers (ACF-MAP-004 API)."""
        self.draw_map()

    def set_projection(self, name: str) -> None:
        """Update map projection and re-render, preserving the current
        zoom/pan extent rather than silently resetting it to the whole
        world on every projection switch."""
        self.projection_manager.set_projection(name)
        self.rebuild_axes()
        self.draw_map()
        self._apply_camera_extent()

    def set_title(self, title: str) -> None:
        """Update map title and trigger redraw."""
        self.title_text = title
        if self.axes is not None:
            self.axes.set_title(title, fontsize=10, color="#7ad4ff", weight="bold", pad=6)
            if self.canvas is not None:
                try:
                    self.canvas.draw_idle()
                except RuntimeError:
                    pass

    def set_active_layers(self, layers: list[str]) -> None:
        """Update active scientific layer catalog and re-render overlays."""
        self.layer_manager.set_active_layers(layers)
        self.draw_map()

    def load_dataset(self, dataset: Dataset) -> None:
        """Connect canonical NWP Dataset (WRF/ARPEGE/ICON/GRIB/NetCDF) to map layers (ACF-MAP-005)."""
        self.layer_manager.bind_dataset(dataset)
        self.draw_map()

    def refresh(self) -> None:
        """Refresh canvas drawing."""
        if self.canvas is not None:
            try:
                self.canvas.draw_idle()
            except RuntimeError:
                pass

    def clear(self) -> None:
        """Clear map axes."""
        if self.axes is not None:
            self.axes.clear()
            self.refresh()

    def resizeEvent(self, event: Any) -> None:
        """Handle widget resize event gracefully."""
        super().resizeEvent(event)
        self.refresh()

    def closeEvent(self, event: Any) -> None:
        """Clean up Matplotlib resources upon widget closure."""
        if self.figure is not None:
            plt.close(self.figure)
        super().closeEvent(event)
