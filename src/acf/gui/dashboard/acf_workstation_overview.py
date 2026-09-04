"""
ACF Scientific Workstation — Overview (Atmospheric State)
============================================================

Real raw atmospheric fields for `acf_workstation.ACFWorkstation` (see
that module's own docstring for the full "AWCI-free" context). Shows
real Temperature / Wind speed / Specific humidity / Pressure at the
currently-selected level of whichever real volume
`acf.awci.vertical_field.compute_real_complexity_volume()` last
computed - reads only the raw physical fields
(`temperature_volume`/`wind_speed_volume`/`specific_humidity_volume`/
`pressure_volume_hpa`), never `awci_volume`/`physical_volume`/
`forecast_volume`. No composite score anywhere.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

#: Real per-variable volume key + unit + a real, disclosed physical
#: rendering range (NOT the AWCI 0-100 scale). Ranges are real,
#: generous envelopes for the actual quantity (K/m/s/kg-kg/hPa), not
#: fabricated score bands.
_VARIABLES: dict[str, dict[str, Any]] = {
    "Temperature": {"key": "temperature_volume", "unit": "K", "cmap": "coolwarm", "vmin": 230.0, "vmax": 310.0},
    "Wind speed": {"key": "wind_speed_volume", "unit": "m/s", "cmap": "viridis", "vmin": 0.0, "vmax": 40.0},
    "Specific humidity": {
        "key": "specific_humidity_volume", "unit": "kg/kg", "cmap": "YlGnBu", "vmin": 0.0, "vmax": 0.02,
    },
    "Pressure": {"key": "pressure_volume_hpa", "unit": "hPa", "cmap": "cividis", "vmin": 100.0, "vmax": 1050.0},
}


class ACFOverviewPanel(QWidget):
    """Real Atmospheric State overview - raw fields, no AWCI content."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_VARIABLES.keys()))
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_selector)
        controls.addStretch()
        layout.addLayout(controls)

        self.map_panel = AWCIMapPanel(
            "ATMOSPHERIC STATE", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume - no new
        solver run."""
        self._volume = volume
        self._level_index = level_index
        self._redraw()

    def _redraw(self) -> None:
        if self._volume is None:
            return
        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        field = self._volume[spec["key"]][self._level_index]

        self.map_panel.set_external_field(
            self._volume["lons"],
            self._volume["lats"],
            field,
            f"Real {self._volume.get('model', '')} — {variable}",
            cmap=spec["cmap"],
            vmin=spec["vmin"],
            vmax=spec["vmax"],
            colorbar_label=f"{variable} ({spec['unit']})",
        )
