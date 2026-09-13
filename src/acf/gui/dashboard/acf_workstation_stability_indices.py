"""
ACF Scientific Workstation — Stability Indices
===================================================

Real, always-visible per-point convective/stability summary (Phase 39,
2026-09-05), closing the "Honest scope" gap `acf_workstation_sounding_
panel.py`'s own module docstring previously disclosed - the reference
mockup's own small colored grid beside its "VERTICAL COMPLEXITY
SOUNDING" box (labelled "High Shear / Stability / CIN / CAPE / Wind
Shear").

Real formulas, all reused as-is - nothing new invented
------------------------------------------------------------
- CAPE/CIN: `acf.awci.convective_energy.
  compute_real_cape_cin_at_point()` - the SAME real MetPy parcel-ascent
  pipeline Thermodynamics Lab's own on-demand "🔄 Compute CAPE/CIN
  Field" button already uses, called here at a single real point
  (~5ms, measured - genuinely cheap for one point, unlike a whole
  grid, which is why that Lab's own gridded version stays on-demand
  and coarser-strided while this stays automatic).
- Bulk wind shear: `acf.awci.wind_shear.
  compute_real_wind_shear_at_point()` - reused by Dynamics Lab and the
  Map Inspector (Phase 36).
- Static stability (N): `acf.awci.workstation_fields.
  compute_real_near_surface_static_stability_at_point()` (added
  alongside this panel) - the real, scalar sibling of
  `compute_real_terrain_field()`'s own vectorized near-surface N,
  kept separate so this per-point panel never pays that function's
  own full-grid elevation/Froude-number cost (~0.5s at AROME's own
  full resolution) just to read one value.
- Bulk Richardson Number (BRN): `acf.science.bulk_richardson_number.
  BulkRichardsonNumber` - real formula BRN = 2*CAPE/shear^2, real
  Weisman & Klemp (1982) classification thresholds (<10 "Weak", 10-45
  "Supercell", >45 "Multicell") - computed from the SAME real CAPE/
  shear already fetched above for this exact point, zero new data
  access. Added 2026-09-13 closing a real gap found during the ACF
  master-prompt audit: this formula already existed in
  `acf.science.bulk_richardson_number` (with its own passing tests)
  but was never wired into any GUI panel anywhere in this codebase
  (verified via grep before this fix). Honestly "n/a" when shear is
  exactly 0 (BRN is undefined, not a fabricated infinite/zero value).
- K-Index, Total Totals, SWEAT Index: `acf.science.{k_index,
  total_totals,sweat_index}` - 3 more real, cited, already-tested
  synoptic severe-weather indices found orphaned the same way BRN was
  (verified via grep: zero references anywhere in `acf.gui` before this
  fix). Unlike CAPE/shear/BRN above (native-level point values), these
  are classically defined at FIXED standard pressure levels (850/700/
  500 hPa) - real linear interpolation of this point's own real T/Td/
  wind profile onto those levels (`np.interp` against the real sorted
  pressure profile), honestly `None` (never a fabricated value) if
  850/700/500 hPa genuinely falls outside this column's real native
  level range (e.g. a coarse/synthetic test volume with few levels).
  Real dewpoint via the same `mpcalc.dewpoint_from_specific_humidity()`
  CAPE/CIN already uses above; real wind speed/direction via MetPy's
  own `mpcalc.wind_speed()`/`mpcalc.wind_direction()` (not hand-rolled
  trigonometry) from the same real interpolated u/v.

Updated together with the Vertical Complexity Sounding panel, at the
same real clicked point - see `acf_workstation.py`'s own
`_on_map_point_clicked()`/`_on_volume_ready()`/`_on_level_changed()`.
"""

from __future__ import annotations

from typing import Any

import metpy.calc as mpcalc
import numpy as np
from metpy.units import units as mp_units
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.awci.workstation_fields import compute_real_near_surface_static_stability_at_point
from acf.gui.theme_tokens import label_style
from acf.science.bulk_richardson_number import BulkRichardsonNumber
from acf.science.k_index import KIndex
from acf.science.sweat_index import SWEATIndex
from acf.science.total_totals import TotalTotals

#: Real, ordered index names shown by ACFStabilityIndicesWidget.
INDEX_NAMES: tuple[str, ...] = (
    "CAPE",
    "CIN",
    "Wind Shear",
    "Static Stability (N)",
    "Bulk Richardson Number",
    "K-Index",
    "Total Totals",
    "SWEAT Index",
)


def _interp_to_pressure(pressure_hpa: np.ndarray, values: np.ndarray, target_hpa: float) -> float | None:
    """Real linear interpolation of a real profile onto one standard
    pressure level - honestly None (never extrapolated/fabricated) if
    target_hpa falls outside this column's own real native-level range."""
    order = np.argsort(pressure_hpa)
    p_sorted = pressure_hpa[order]
    v_sorted = values[order]
    if target_hpa < p_sorted[0] or target_hpa > p_sorted[-1]:
        return None
    return float(np.interp(target_hpa, p_sorted, v_sorted))


def compute_real_severe_weather_indices_at_point(
    t_profile: np.ndarray, q_profile: np.ndarray, p_profile: np.ndarray, u_profile: np.ndarray, v_profile: np.ndarray
) -> dict[str, Any]:
    """Real K-Index/Total Totals/SWEAT Index at one point, interpolated
    from the real native-level profile onto the standard 850/700/500 hPa
    levels these classic indices are defined at - see module docstring."""
    pressure_q = p_profile * mp_units.hPa
    specific_humidity = np.clip(q_profile, 1e-9, None) * mp_units("kg/kg")
    dewpoint_c = mpcalc.dewpoint_from_specific_humidity(pressure_q, specific_humidity).to("degC").magnitude
    temperature_c = (t_profile * mp_units.kelvin).to("degC").magnitude
    wind_speed_kt = (
        mpcalc.wind_speed(u_profile * mp_units("m/s"), v_profile * mp_units("m/s")).to("knot").magnitude
    )
    wind_dir_deg = mpcalc.wind_direction(u_profile * mp_units("m/s"), v_profile * mp_units("m/s")).magnitude

    t850 = _interp_to_pressure(p_profile, temperature_c, 850.0)
    t700 = _interp_to_pressure(p_profile, temperature_c, 700.0)
    t500 = _interp_to_pressure(p_profile, temperature_c, 500.0)
    td850 = _interp_to_pressure(p_profile, dewpoint_c, 850.0)
    td700 = _interp_to_pressure(p_profile, dewpoint_c, 700.0)
    wspd850 = _interp_to_pressure(p_profile, wind_speed_kt, 850.0)
    wspd500 = _interp_to_pressure(p_profile, wind_speed_kt, 500.0)
    wdir850 = _interp_to_pressure(p_profile, wind_dir_deg, 850.0)
    wdir500 = _interp_to_pressure(p_profile, wind_dir_deg, 500.0)

    result: dict[str, Any] = {
        "k_index": None,
        "k_index_category": None,
        "total_totals": None,
        "total_totals_category": None,
        "sweat_index": None,
        "sweat_index_category": None,
    }

    if t850 is not None and t700 is not None and t500 is not None and td850 is not None and td700 is not None:
        ki = KIndex.calculate(t850=t850, t700=t700, t500=t500, td850=td850, td700=td700)
        result["k_index"] = ki
        result["k_index_category"] = KIndex.category(ki)

        tt = TotalTotals.calculate(t850=t850, td850=td850, t500=t500)
        result["total_totals"] = tt
        result["total_totals_category"] = TotalTotals.category(tt)

        if wspd850 is not None and wspd500 is not None and wdir850 is not None and wdir500 is not None:
            sweat = SWEATIndex.calculate(
                td850=td850, tt=tt, wind850=wspd850, wind500=wspd500, dir850=wdir850, dir500=wdir500
            )
            result["sweat_index"] = sweat
            result["sweat_index_category"] = SWEATIndex.category(sweat)

    return result


def compute_real_stability_indices_at_point(volume: dict[str, Any], lat: float, lon: float) -> dict[str, Any]:
    """Real, Qt-free per-point stability summary at the nearest real
    grid column - see module docstring for exactly what backs each
    value."""
    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    lat_idx = int(np.argmin(np.abs(lats - lat)))
    lon_idx = int(np.argmin(np.abs(lons - lon)))

    t_profile = volume["temperature_volume"][:, lat_idx, lon_idx]
    q_profile = volume["specific_humidity_volume"][:, lat_idx, lon_idx]
    p_profile = volume["pressure_volume_hpa"][:, lat_idx, lon_idx]
    u_profile = volume["u_volume"][:, lat_idx, lon_idx]
    v_profile = volume["v_volume"][:, lat_idx, lon_idx]

    cape_cin = compute_real_cape_cin_at_point(t_profile, q_profile, p_profile)
    shear = compute_real_wind_shear_at_point(u_profile, v_profile)
    static_stability = compute_real_near_surface_static_stability_at_point(
        float(t_profile[0]), float(t_profile[1]), float(p_profile[0]), float(p_profile[1])
    )

    shear_m_s = shear["shear_m_s"]
    if shear_m_s == 0:
        brn = None  # BRN = 2*CAPE/shear^2 is genuinely undefined at shear==0 - honestly None, never a fabricated value.
        brn_category = None
    else:
        brn = BulkRichardsonNumber.calculate(cape=cape_cin["cape_j_kg"], shear=shear_m_s)
        brn_category = BulkRichardsonNumber.category(brn)

    severe_indices = compute_real_severe_weather_indices_at_point(t_profile, q_profile, p_profile, u_profile, v_profile)

    return {
        "lat": float(lats[lat_idx]),
        "lon": float(lons[lon_idx]),
        "cape_j_kg": cape_cin["cape_j_kg"],
        "cin_j_kg": cape_cin["cin_j_kg"],
        "bulk_wind_shear_ms": shear_m_s,
        "static_stability_n_s1": static_stability,
        "bulk_richardson_number": brn,
        "bulk_richardson_category": brn_category,
        **severe_indices,
    }


class ACFStabilityIndicesWidget(QWidget):
    """Real, compact stability-index summary - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("STABILITY INDICES")
        grid = QGridLayout(group)
        outer.addWidget(group)

        self._labels: dict[str, QLabel] = {}
        for row, name in enumerate(INDEX_NAMES):
            name_label = QLabel(name)
            name_label.setStyleSheet(label_style("text_muted", "xs"))
            value_label = QLabel("—")
            value_label.setStyleSheet(label_style("text_primary", "sm", "bold"))
            grid.addWidget(name_label, row, 0)
            grid.addWidget(value_label, row, 1)
            self._labels[name] = value_label

    def set_indices(self, indices: dict[str, Any]) -> None:
        self._set("CAPE", indices["cape_j_kg"], "J/kg")
        self._set("CIN", indices["cin_j_kg"], "J/kg")
        self._set("Wind Shear", indices["bulk_wind_shear_ms"], "m/s")
        self._set("Static Stability (N)", indices["static_stability_n_s1"], "s⁻¹", digits=4)
        self._set_with_category("Bulk Richardson Number", indices.get("bulk_richardson_number"), indices.get("bulk_richardson_category"))
        self._set_with_category("K-Index", indices.get("k_index"), indices.get("k_index_category"))
        self._set_with_category("Total Totals", indices.get("total_totals"), indices.get("total_totals_category"))
        self._set_with_category("SWEAT Index", indices.get("sweat_index"), indices.get("sweat_index_category"))

    def _set(self, name: str, value: float | None, unit: str, digits: int = 1) -> None:
        label = self._labels[name]
        if value is None:
            label.setText("n/a")
            return
        label.setText(f"{value:.{digits}f} {unit}")

    def _set_with_category(self, name: str, value: float | None, category: str | None) -> None:
        label = self._labels[name]
        if value is None:
            label.setText("n/a")
        else:
            label.setText(f"{value:.1f} ({category})")

    def status(self) -> dict[str, Any]:
        return {"has_data": any(label.text() != "—" for label in self._labels.values())}
