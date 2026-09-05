"""Central Earth View & Projections Manager supporting Phase 3 & Phase 4 Scientific Layers (ACF-UI-013)."""

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from acf.gui.map.map_canvas import MapCanvas

#: Real responsive-sizing fix (2026-09-05): QComboBox's default
#: `AdjustToContentsOnFirstShow` policy makes its *minimum* size hint
#: wide enough for its single longest item, in full, with no eliding -
#: "Comparison View (Obs vs Model)"/"Sea Ice Concentration & Thickness"
#: here. Measured effect: this control bar's own minimumSizeHint() was
#: (800, 30), floored almost entirely by these two combos plus their
#: labels, which floors ESOCWindow's central widget - and so the whole
#: ESOC window - at that width no matter the operator's screen size.
#: `AdjustToMinimumContentsLengthWithIcon` instead floors the box at a
#: fixed character count, letting it shrink further and elide ("...")
#: the closed box's text when squeezed - standard Qt behaviour, and the
#: dropdown popup itself still always shows every item's full text.
_COMBO_MIN_CONTENTS_LENGTH = 16


def _shrink_combo_min_width(combo: QComboBox) -> None:
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(_COMBO_MIN_CONTENTS_LENGTH)


class ViewManager(QWidget):
    """Manages Phase 3 Earth View Projections & Phase 4 Scientific Layer Catalog."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Control Bar for Map Projections & View Modes
        ctrl_bar = QWidget()
        c_layout = QHBoxLayout(ctrl_bar)
        c_layout.setContentsMargins(4, 4, 4, 4)

        lbl_proj = QLabel("View Projection / Mode: ")
        lbl_proj.setStyleSheet("font-weight: bold; color: #81D4FA;")
        c_layout.addWidget(lbl_proj)

        self.combo_view_mode = QComboBox()
        self.view_modes = [
            "2D Mercator Map",
            "3D Photorealistic Sphere",
            "Global Interactive Globe",
            "Orthographic Projection",
            "Lambert Conformal Conic",
            "Polar North Stereographic",
            "Polar South Stereographic",
            "Split Screen (Left/Right)",
            "Comparison View (Obs vs Model)",
            "Swipe View",
            "Historical Replay",
            "Future Projection",
            "Digital Twin 4D View",
            "Scenario Viewer",
            "Earth Animation Player",
        ]
        self.combo_view_mode.addItems(self.view_modes)
        self.combo_view_mode.currentTextChanged.connect(self._on_view_mode_changed)
        _shrink_combo_min_width(self.combo_view_mode)
        c_layout.addWidget(self.combo_view_mode)

        lbl_layer = QLabel("Quick Layer Toggle: ")
        lbl_layer.setStyleSheet("font-weight: bold; color: #AED581;")
        c_layout.addWidget(lbl_layer)

        self.combo_quick_layer = QComboBox()
        self.scientific_layers = [
            "2m Temperature (°C)",
            "Mean Sea Level Pressure (MSLP)",
            "10m Wind Speed & Gusts",
            "Cloud Cover & Precipitable Water",
            "CAPE & CIN Instability",
            "Radar Reflectivity Mosaic",
            "Satellite RGB / IR / Water Vapor",
            "Sea Surface Temperature (SST)",
            "Sea Ice Concentration & Thickness",
            "Ocean Currents & Wave Height",
            "River Flow & Flood Inundation",
            "Soil Moisture & NDVI / LAI",
            "Fire Weather Index & Smoke Plumes",
            "Dust & PM2.5 / PM10 Air Quality",
            "Ozone, NO2 & CO2 Carbon Flux",
            "Planetary Boundaries Audit Layer",
        ]
        self.combo_quick_layer.addItems(self.scientific_layers)
        self.combo_quick_layer.currentTextChanged.connect(self._on_quick_layer_changed)
        _shrink_combo_min_width(self.combo_quick_layer)
        c_layout.addWidget(self.combo_quick_layer)

        layout.addWidget(ctrl_bar)

        self.map_canvas = MapCanvas()
        layout.addWidget(self.map_canvas)

        self.active_layers: list[str] = [
            "Satellite RGB",
            "Radar Mosaic",
            "2m Temp",
            "Wind Vectors",
            "MSLP",
        ]
        self.current_view_mode: str = "2D Mercator Map"

    def _on_view_mode_changed(self, mode_name: str) -> None:
        self.current_view_mode = mode_name
        self.map_canvas.set_projection(mode_name)
        self.map_canvas.label.setText(f"🌍 ACF MAP CANVAS [{mode_name.upper()}]")

    def _on_quick_layer_changed(self, layer_name: str) -> None:
        if layer_name not in self.active_layers:
            self.active_layers.append(layer_name)
            self.map_canvas.set_active_layers(self.active_layers)

    def set_layers(self, layers: list[str]) -> None:
        """Synchronize active map layer list."""
        self.active_layers = layers
        self.map_canvas.set_active_layers(layers)

    def toggle_layer(self, layer_name: str) -> list[str]:
        """Toggle inclusion of layer_name in active_layers list."""
        if layer_name in self.active_layers:
            self.active_layers.remove(layer_name)
        else:
            self.active_layers.append(layer_name)
        self.map_canvas.set_active_layers(self.active_layers)
        return self.active_layers
