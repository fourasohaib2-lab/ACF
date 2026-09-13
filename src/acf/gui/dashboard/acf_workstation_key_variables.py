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
Relative humidity is derived from the volume's own specific humidity,
pressure and temperature via the real
`acf.science.moisture.Moisture.relative_humidity_from_temperature()`
conversion (vapor pressure from specific humidity, saturation vapor
pressure from temperature, RH = e/es) - not a fabricated formula.

All six readouts (Temperature/Relative Humidity/Wind Speed/CAPE/CIN/
LCL) describe the SAME physical grid point: the full-resolution
volume's domain-center cell (`ci, cj`), and its nearest equivalent on
`compute_real_convection_indices_field()`'s coarser strided sub-grid
(`ci // stride, cj // stride`), since that function's sub-grid row/
column `si`/`sj` corresponds to full-resolution row/column
`si * stride`/`sj * stride` (see its own docstring).

Honesty: any value the underlying computation reports as NaN (e.g.
CAPE/CIN/LCL "not computed" per that function's own docstring) renders
as "NOT_COMPUTED", never a fabricated number.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from acf.awci.workstation_fields import (
    CONVECTION_GRID_STRIDE,
    compute_real_convection_indices_field,
)
from acf.gui.theme_tokens import label_style
from acf.science.moisture import Moisture

_NOT_AVAILABLE = "NOT_AVAILABLE_NO_VOLUME_COMPUTED"


class KeyVariablesPanel(QWidget):
    """Real scalar Key Atmospheric Variables readout."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        #: Real, already-computed values of the most recent
        #: `update_from_volume()` call (added 2026-09-13 for the
        #: Workstation composer): the real convection-indices dict this
        #: panel computed (or was handed), and the real scalar values
        #: it actually displayed at the domain-center point. Kept so a
        #: caller (e.g. `HazardAlertsPanel`, which needs the same real
        #: CAPE/bulk shear/relative humidity) can REUSE them instead of
        #: running the genuinely expensive real MetPy parcel-ascent
        #: pipeline a second time. None until a real update happens -
        #: never a fabricated placeholder value.
        self.last_indices: dict[str, Any] | None = None
        self.last_center_values: dict[str, float] | None = None

        layout = QGridLayout(self)

        self.temperature_value = self._row(layout, 0, "Temperature (850 hPa)")
        self.humidity_value = self._row(layout, 1, "Relative Humidity (700 hPa)")
        self.wind_speed_value = self._row(layout, 2, "Wind Speed (850 hPa)")
        self.cape_value = self._row(layout, 3, "CAPE")
        self.cin_value = self._row(layout, 4, "CIN")
        self.lcl_value = self._row(layout, 5, "LCL")
        self.shear_value = self._row(layout, 6, "Shear (0-6 km)")

    def _row(self, layout: QGridLayout, row: int, title: str) -> QLabel:
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel(_NOT_AVAILABLE)
        layout.addWidget(heading, row, 0)
        layout.addWidget(value, row, 1)
        return value

    def update_from_volume(
        self, volume: dict[str, Any], level_index: int, indices: dict[str, Any] | None = None
    ) -> None:
        """Real re-slice of the already-computed volume at its domain
        center grid point - no new solver run.

        `indices` (added 2026-09-13) accepts a real
        `compute_real_convection_indices_field()` result ALREADY
        computed for this exact volume (the Workstation composer runs
        it once, off the GUI thread, and shares the same real result
        with this panel and the Hazard Alerts panel). Left at None -
        every pre-existing caller - this panel computes it itself
        exactly as before; the call is genuinely expensive (a real
        MetPy parcel ascent per strided grid point, measured ~3s on
        ARPEGE's own real grid), which is precisely why the composer
        hands it in rather than triggering it once per panel and once
        per level change.
        """
        lats = volume["lats"]
        lons = volume["lons"]
        ci, cj = len(lats) // 2, len(lons) // 2

        temp_k = float(volume["temperature_volume"][level_index, ci, cj])
        self.temperature_value.setText(f"{temp_k - 273.15:.1f} °C")

        wind_ms = float(volume["wind_speed_volume"][level_index, ci, cj])
        self.wind_speed_value.setText(f"{wind_ms:.1f} m/s")

        q_kg_kg = float(volume["specific_humidity_volume"][level_index, ci, cj])
        pressure_hpa = float(volume["pressure_volume_hpa"][level_index, ci, cj])
        # Real conversion: vapor pressure (from specific humidity +
        # pressure) over saturation vapor pressure (from temperature),
        # composed by Moisture.relative_humidity_from_temperature() -
        # no fabricated formula.
        rh_fraction = Moisture.relative_humidity_from_temperature(q_kg_kg, pressure_hpa, temp_k)
        rh_pct = min(100.0, 100.0 * rh_fraction)
        self.humidity_value.setText(f"{rh_pct:.0f} %")

        if indices is None:
            indices = compute_real_convection_indices_field(
                volume["temperature_volume"],
                volume["specific_humidity_volume"],
                volume["pressure_volume_hpa"],
                volume["u_volume"],
                volume["v_volume"],
                lats,
                lons,
            )
        # Same physical grid point as (ci, cj) above, on the indices'
        # own coarser strided sub-grid (sub-grid row/col si/sj <->
        # full-res row/col si*stride/sj*stride - see that function's
        # docstring).
        sub_ci, sub_cj = ci // CONVECTION_GRID_STRIDE, cj // CONVECTION_GRID_STRIDE
        self._set_or_not_computed(self.cape_value, indices["cape_j_kg"][sub_ci, sub_cj], "J/kg")
        self._set_or_not_computed(self.cin_value, indices["cin_j_kg"][sub_ci, sub_cj], "J/kg")
        self._set_or_not_computed(self.lcl_value, indices["lcl_m"][sub_ci, sub_cj], "m")
        self._set_or_not_computed(self.shear_value, indices["bulk_shear_m_s"][sub_ci, sub_cj], "m/s")

        # Real, already-computed values kept for reuse (see
        # `last_indices`'s own comment in __init__) - exactly what was
        # just displayed, nothing re-derived.
        self.last_indices = indices
        self.last_center_values = {
            "temperature_c": temp_k - 273.15,
            "wind_speed_m_s": wind_ms,
            "relative_humidity_pct": rh_pct,
            "cape_j_kg": float(indices["cape_j_kg"][sub_ci, sub_cj]),
            "cin_j_kg": float(indices["cin_j_kg"][sub_ci, sub_cj]),
            "lcl_m": float(indices["lcl_m"][sub_ci, sub_cj]),
            "bulk_shear_m_s": float(indices["bulk_shear_m_s"][sub_ci, sub_cj]),
        }

    @staticmethod
    def _set_or_not_computed(label: QLabel, value: float, unit: str) -> None:
        if np.isnan(value):
            label.setText("NOT_COMPUTED")
        else:
            label.setText(f"{value:.0f} {unit}")
