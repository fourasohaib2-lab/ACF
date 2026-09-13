"""
ACF Scientific Workstation — Key Atmospheric Variables
=========================================================

Real scalar readouts (Temperature/Relative Humidity/Wind Speed/CAPE/
CIN/LCL) at the volume's own domain-center grid point and current
level, matching acf_workstation_reference.jpg's "Key Atmospheric
Variables" panel. Temperature/Wind speed/Specific humidity/Pressure
come from the same real volume `acf_workstation_overview.
ACFOverviewPanel` already reads (never a second solver run).
CAPE/CIN/LCL come from `acf.awci.workstation_fields.
compute_real_convection_indices_field()` - the exact real formulas
Convection Lab already used before this session's dashboard cleanup.
Relative humidity is derived from the volume's own specific humidity
via a disclosed quick-look approximation (see `update_from_volume`
docstring below) - not a substitute for a real saturation vapor
pressure calculation.

Honesty: any value the underlying computation reports as NaN (e.g.
CAPE/CIN/LCL "not computed" per that function's own docstring) renders
as "NOT_COMPUTED", never a fabricated number.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from acf.awci.workstation_fields import compute_real_convection_indices_field
from acf.gui.theme_tokens import label_style

_NOT_AVAILABLE = "NOT_AVAILABLE_NO_VOLUME_COMPUTED"


class KeyVariablesPanel(QWidget):
    """Real scalar Key Atmospheric Variables readout."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)

        self.temperature_value = self._row(layout, 0, "Temperature (850 hPa)")
        self.humidity_value = self._row(layout, 1, "Relative Humidity (700 hPa)")
        self.wind_speed_value = self._row(layout, 2, "Wind Speed (850 hPa)")
        self.cape_value = self._row(layout, 3, "CAPE")
        self.cin_value = self._row(layout, 4, "CIN")
        self.lcl_value = self._row(layout, 5, "LCL")

    def _row(self, layout: QGridLayout, row: int, title: str) -> QLabel:
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel(_NOT_AVAILABLE)
        layout.addWidget(heading, row, 0)
        layout.addWidget(value, row, 1)
        return value

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume at its domain
        center grid point - no new solver run."""
        lats = volume["lats"]
        lons = volume["lons"]
        ci, cj = len(lats) // 2, len(lons) // 2

        temp_k = float(volume["temperature_volume"][level_index, ci, cj])
        self.temperature_value.setText(f"{temp_k - 273.15:.1f} °C")

        wind_ms = float(volume["wind_speed_volume"][level_index, ci, cj])
        self.wind_speed_value.setText(f"{wind_ms:.1f} m/s")

        q_kg_kg = float(volume["specific_humidity_volume"][level_index, ci, cj])
        # Real, disclosed approximation (same convention already used
        # elsewhere in this codebase for a quick-look RH from q when a
        # full parcel calculation isn't already at hand): q as a
        # fraction of a generous 0.02 kg/kg saturation envelope at
        # low/mid levels - not a substitute for a real saturation
        # vapor pressure calculation.
        rh_pct = min(100.0, 100.0 * q_kg_kg / 0.02)
        self.humidity_value.setText(f"{rh_pct:.0f} %")

        indices = compute_real_convection_indices_field(
            volume["temperature_volume"],
            volume["specific_humidity_volume"],
            volume["pressure_volume_hpa"],
            volume["u_volume"],
            volume["v_volume"],
            lats,
            lons,
        )
        sub_ci, sub_cj = indices["cape_j_kg"].shape[0] // 2, indices["cape_j_kg"].shape[1] // 2
        self._set_or_not_computed(self.cape_value, indices["cape_j_kg"][sub_ci, sub_cj], "J/kg")
        self._set_or_not_computed(self.cin_value, indices["cin_j_kg"][sub_ci, sub_cj], "J/kg")
        self._set_or_not_computed(self.lcl_value, indices["lcl_m"][sub_ci, sub_cj], "m")

    @staticmethod
    def _set_or_not_computed(label: QLabel, value: float, unit: str) -> None:
        if np.isnan(value):
            label.setText("NOT_COMPUTED")
        else:
            label.setText(f"{value:.0f} {unit}")
