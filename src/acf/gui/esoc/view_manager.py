"""Central Earth View & Projections Manager supporting Phase 3 & Phase 4 Scientific Layers (ACF-UI-013)."""

from typing import List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Qt


class CentralMapCanvasPlaceholder(QWidget):
    """Central interactive Earth Map Canvas display placeholder."""

    def __init__(self, title: str = "GLOBAL EARTH INTERACTIVE MAP") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(f"🌍 {title}")
        self.label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #81D4FA; border: 2px dashed #0288D1; padding: 20px;"
        )
        layout.addWidget(self.label)

        self.layer_info = QLabel("Active Layers: Satellite RGB | Radar Mosaic | 2m Temp | Wind Vectors | MSLP")
        self.layer_info.setStyleSheet("color: #B0BEC5; font-size: 11px;")
        layout.addWidget(self.layer_info)

    def set_active_layers(self, layers: List[str]) -> None:
        """Update layer info display text."""
        self.layer_info.setText("Active Layers: " + " | ".join(layers))


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
        c_layout.addWidget(self.combo_quick_layer)

        layout.addWidget(ctrl_bar)

        self.map_canvas = CentralMapCanvasPlaceholder("ACF UNIFIED EARTH SYSTEM MAP CANVAS")
        layout.addWidget(self.map_canvas)

        self.active_layers: List[str] = [
            "Satellite RGB",
            "Radar Mosaic",
            "2m Temp",
            "Wind Vectors",
            "MSLP",
        ]
        self.current_view_mode: str = "2D Mercator Map"

    def _on_view_mode_changed(self, mode_name: str) -> None:
        self.current_view_mode = mode_name
        self.map_canvas.label.setText(f"🌍 ACF MAP CANVAS [{mode_name.upper()}]")

    def _on_quick_layer_changed(self, layer_name: str) -> None:
        if layer_name not in self.active_layers:
            self.active_layers.append(layer_name)
            self.map_canvas.set_active_layers(self.active_layers)

    def set_layers(self, layers: List[str]) -> None:
        """Synchronize active map layer list."""
        self.active_layers = layers
        self.map_canvas.set_active_layers(layers)

    def toggle_layer(self, layer_name: str) -> List[str]:
        """Toggle inclusion of layer_name in active_layers list."""
        if layer_name in self.active_layers:
            self.active_layers.remove(layer_name)
        else:
            self.active_layers.append(layer_name)
        self.map_canvas.set_active_layers(self.active_layers)
        return self.active_layers
