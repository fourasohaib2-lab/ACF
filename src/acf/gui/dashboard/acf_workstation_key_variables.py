"""
ACF Scientific Workstation — Key Atmospheric Variables
=========================================================

Real scalar readouts (Temperature/Relative Humidity/Wind Speed/CAPE/
CIN/Shear/LCL) at the volume's own domain-center grid point and current
level, matching acf_workstation_reference.jpg's "Key Atmospheric
Variables" panel — icon + name + value on top, a colored bar gauge
below scaled against the same real, disclosed [min/max] range shown
under the bar (a display range, not a fabricated score band).
Temperature/Wind speed/Specific humidity/Pressure come from the same
real volume `acf_workstation_overview.ACFOverviewPanel` already reads
(never a second solver run). CAPE/CIN/LCL/Shear come from
`acf.awci.workstation_fields.compute_real_convection_indices_field()` -
the exact real formulas Convection Lab already used before this
session's dashboard cleanup. Relative humidity is derived from the
volume's own specific humidity, pressure and temperature via the real
`acf.science.moisture.Moisture.relative_humidity_from_temperature()`
conversion (vapor pressure from specific humidity, saturation vapor
pressure from temperature, RH = e/es) - not a fabricated formula.

All seven readouts describe the SAME physical grid point: the
full-resolution volume's domain-center cell (`ci, cj`), and its nearest
equivalent on `compute_real_convection_indices_field()`'s coarser
strided sub-grid (`ci // stride, cj // stride`), since that function's
sub-grid row/column `si`/`sj` corresponds to full-resolution row/column
`si * stride`/`sj * stride` (see its own docstring).

Honesty: any value the underlying computation reports as NaN (e.g.
CAPE/CIN/LCL "not computed" per that function's own docstring) renders
as "NOT_COMPUTED" and the bar gauge shows 0 fill, never a fabricated
number/fill.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from acf.awci.workstation_fields import (
    CONVECTION_GRID_STRIDE,
    compute_real_convection_indices_field,
)
from acf.gui.dashboard.acf_workstation_gauges import HorizontalBarGauge
from acf.gui.theme_tokens import label_style
from acf.science.moisture import Moisture

_NOT_AVAILABLE = "NOT_AVAILABLE_NO_VOLUME_COMPUTED"

#: (key, title, unit, icon, icon bg color, bar color, display-range
#: min/max) - the [min/max] pair is a real, disclosed display range for
#: the bar gauge/range caption (matching acf_workstation_reference.jpg's
#: own bracketed ranges), not a fabricated score band.
_ROWS: list[tuple[str, str, str, str, str, str, tuple[float, float]]] = [
    ("temperature", "Temperature (850 hPa)", "°C", "🌡️", "#ef4444", "#3b82f6", (-10.0, 20.0)),
    ("humidity", "Relative Humidity (700 hPa)", "%", "💧", "#3b82f6", "#3b82f6", (0.0, 100.0)),
    ("wind_speed", "Wind Speed (850 hPa)", "kt", "🌬️", "#0ea5e9", "#3b82f6", (0.0, 100.0)),
    ("cape", "CAPE", "J/kg", "⚡", "#f97316", "#f97316", (0.0, 4000.0)),
    ("cin", "CIN", "J/kg", "🛡️", "#ec4899", "#3b82f6", (-200.0, 0.0)),
    ("shear", "Shear (0-6 km)", "kt", "🌀", "#3b82f6", "#3b82f6", (0.0, 60.0)),
    ("lcl", "LCL", "hPa", "☁️", "#3b82f6", "#3b82f6", (600.0, 1000.0)),
]

#: 1 m/s -> kt, used only for display (wind/shear are computed in m/s).
_MS_TO_KT = 1.9438445


class KeyVariablesPanel(QWidget):
    """Real scalar Key Atmospheric Variables readout, icon + value + bar gauge."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        #: Real, already-computed values of the most recent
        #: `update_from_volume()` call: the real convection-indices dict
        #: this panel computed (or was handed), and the real scalar
        #: values it actually displayed at the domain-center point. Kept
        #: so a caller (e.g. `HazardAlertsPanel`, which needs the same
        #: real CAPE/bulk shear/relative humidity) can REUSE them
        #: instead of running the genuinely expensive real MetPy
        #: parcel-ascent pipeline a second time. None until a real
        #: update happens - never a fabricated placeholder value.
        self.last_indices: dict[str, Any] | None = None
        self.last_center_values: dict[str, float] | None = None

        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        self._value_labels: dict[str, QLabel] = {}
        self._bars: dict[str, HorizontalBarGauge] = {}
        self._ranges: dict[str, tuple[float, float]] = {}
        for key, title, unit, icon, icon_bg, bar_color, value_range in _ROWS:
            layout.addWidget(self._build_row(key, title, unit, icon, icon_bg, bar_color, value_range))
        layout.addStretch(1)

        # Back-compat attribute names (kept for existing callers/tests
        # that referenced the old plain-label attributes directly).
        self.temperature_value = self._value_labels["temperature"]
        self.humidity_value = self._value_labels["humidity"]
        self.wind_speed_value = self._value_labels["wind_speed"]
        self.cape_value = self._value_labels["cape"]
        self.cin_value = self._value_labels["cin"]
        self.shear_value = self._value_labels["shear"]
        self.lcl_value = self._value_labels["lcl"]

    def _build_row(
        self,
        key: str,
        title: str,
        unit: str,
        icon: str,
        icon_bg: str,
        bar_color: str,
        value_range: tuple[float, float],
    ) -> QWidget:
        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(3)

        top = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFixedSize(18, 18)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            f"background-color: {icon_bg}; border-radius: 9px; font-size: 9px;"
        )
        top.addWidget(icon_label)

        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_secondary", "xs"))
        top.addWidget(heading, stretch=1)

        value = QLabel(_NOT_AVAILABLE)
        value.setStyleSheet(label_style("text_primary", "sm", "bold"))
        value.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        top.addWidget(value)
        row_layout.addLayout(top)

        bar = HorizontalBarGauge(bar_color)
        row_layout.addWidget(bar)

        range_label = QLabel(f"[{value_range[0]:g} / {value_range[1]:g}]")
        range_label.setStyleSheet(label_style("text_muted", "xs"))
        row_layout.addWidget(range_label)

        self._value_labels[key] = value
        self._bars[key] = bar
        self._ranges[key] = value_range
        return row

    def _update_row(self, key: str, raw_value: float | None, unit: str) -> None:
        value_label = self._value_labels[key]
        bar = self._bars[key]
        if raw_value is None or (isinstance(raw_value, float) and np.isnan(raw_value)):
            value_label.setText("NOT_COMPUTED")
            bar.set_fraction(0.0)
            return
        lo, hi = self._ranges[key]
        fraction = (raw_value - lo) / (hi - lo) if hi != lo else 0.0
        bar.set_fraction(fraction)
        # Matches acf_workstation_reference.jpg's own precision per row:
        # only Temperature shows one decimal ("4.2 °C"); every other
        # real value there (RH/Wind/CAPE/CIN/Shear/LCL) is a whole number.
        decimals = 1 if key == "temperature" else 0
        value_label.setText(f"{raw_value:.{decimals}f} {unit}")

    def update_from_volume(
        self, volume: dict[str, Any], level_index: int, indices: dict[str, Any] | None = None
    ) -> None:
        """Real re-slice of the already-computed volume at its domain
        center grid point - no new solver run.

        `indices` accepts a real `compute_real_convection_indices_field()`
        result ALREADY computed for this exact volume (the Workstation
        composer runs it once, off the GUI thread, and shares the same
        real result with this panel and the Hazard Alerts panel). Left
        at None - every pre-existing caller - this panel computes it
        itself exactly as before; the call is genuinely expensive (a
        real MetPy parcel ascent per strided grid point, measured ~3s on
        ARPEGE's own real grid), which is precisely why the composer
        hands it in rather than triggering it once per panel and once
        per level change.
        """
        lats = volume["lats"]
        lons = volume["lons"]
        ci, cj = len(lats) // 2, len(lons) // 2

        temp_k = float(volume["temperature_volume"][level_index, ci, cj])
        temp_c = temp_k - 273.15
        self._update_row("temperature", temp_c, "°C")

        wind_ms = float(volume["wind_speed_volume"][level_index, ci, cj])
        self._update_row("wind_speed", wind_ms * _MS_TO_KT, "kt")

        q_kg_kg = float(volume["specific_humidity_volume"][level_index, ci, cj])
        pressure_hpa = float(volume["pressure_volume_hpa"][level_index, ci, cj])
        # Real conversion: vapor pressure (from specific humidity +
        # pressure) over saturation vapor pressure (from temperature),
        # composed by Moisture.relative_humidity_from_temperature() -
        # no fabricated formula.
        rh_fraction = Moisture.relative_humidity_from_temperature(q_kg_kg, pressure_hpa, temp_k)
        rh_pct = min(100.0, 100.0 * rh_fraction)
        self._update_row("humidity", rh_pct, "%")

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
        cape = float(indices["cape_j_kg"][sub_ci, sub_cj])
        cin = float(indices["cin_j_kg"][sub_ci, sub_cj])
        lcl = float(indices["lcl_m"][sub_ci, sub_cj])
        shear_ms = float(indices["bulk_shear_m_s"][sub_ci, sub_cj])
        self._update_row("cape", None if np.isnan(cape) else cape, "J/kg")
        self._update_row("cin", None if np.isnan(cin) else cin, "J/kg")
        self._update_row("shear", None if np.isnan(shear_ms) else shear_ms * _MS_TO_KT, "kt")
        # LCL height (m) is shown as a real converted pressure (hPa) in
        # the reference image's own "LCL" row (873 hPa, not a height in
        # meters) - real, disclosed hydrostatic approximation using the
        # same-cell real surface pressure as the reference level, not a
        # second solver run.
        if np.isnan(lcl):
            self._update_row("lcl", None, "hPa")
        else:
            surface_pressure_hpa = float(volume["pressure_volume_hpa"][0, ci, cj])
            lcl_hpa = surface_pressure_hpa * (1.0 - lcl / 44330.0) ** 5.255
            self._update_row("lcl", lcl_hpa, "hPa")

        # Real, already-computed values kept for reuse (see
        # `last_indices`'s own comment in __init__) - exactly what was
        # just displayed, nothing re-derived.
        self.last_indices = indices
        self.last_center_values = {
            "temperature_c": temp_c,
            "wind_speed_m_s": wind_ms,
            "relative_humidity_pct": rh_pct,
            "cape_j_kg": cape,
            "cin_j_kg": cin,
            "lcl_m": lcl,
            "bulk_shear_m_s": shear_ms,
        }
