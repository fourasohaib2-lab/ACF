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

Updated together with the Vertical Complexity Sounding panel, at the
same real clicked point - see `acf_workstation.py`'s own
`_on_map_point_clicked()`/`_on_volume_ready()`/`_on_level_changed()`.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.awci.workstation_fields import compute_real_near_surface_static_stability_at_point
from acf.gui.theme_tokens import label_style

#: Real, ordered index names shown by ACFStabilityIndicesWidget.
INDEX_NAMES: tuple[str, ...] = ("CAPE", "CIN", "Wind Shear", "Static Stability (N)")


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

    return {
        "lat": float(lats[lat_idx]),
        "lon": float(lons[lon_idx]),
        "cape_j_kg": cape_cin["cape_j_kg"],
        "cin_j_kg": cape_cin["cin_j_kg"],
        "bulk_wind_shear_ms": shear["shear_m_s"],
        "static_stability_n_s1": static_stability,
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

    def _set(self, name: str, value: float | None, unit: str, digits: int = 1) -> None:
        label = self._labels[name]
        if value is None:
            label.setText("n/a")
            return
        label.setText(f"{value:.{digits}f} {unit}")

    def status(self) -> dict[str, Any]:
        return {"has_data": any(label.text() != "—" for label in self._labels.values())}
