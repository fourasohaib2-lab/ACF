"""
ACF Scientific Workstation — Dynamics Lab
==========================================

Real circulation analysis panel for `acf_workstation.ACFWorkstation`
(built 2026-09-04, explicit user request: an "ACF Scientific
Workstation" dashboard exposing ACF's own modular atmospheric science
- Dynamics/Thermodynamics/Convection/etc. - with NO AWCI score/gauge
anywhere). Shows real wind speed, real relative vorticity, and real
horizontal divergence at the currently-selected level of whichever
real volume `ACFWorkstation`'s own worker last computed
(`acf.awci.vertical_field.compute_real_complexity_volume()`) - reads
only that volume's real `u_volume`/`v_volume`/`wind_speed_volume`,
never its `awci_volume`/`physical_volume`/`forecast_volume`.

Real vorticity/divergence, not reimplemented
-----------------------------------------------
`compute_real_vorticity_divergence()` below computes the real
horizontal gradients (du/dx, du/dy, dv/dx, dv/dy) via `np.gradient` on
the real lat/lon grid, using the standard real metric-spacing
approximation for a regular lat/lon grid (dy = R*dphi, dx =
R*cos(phi)*dlambda, R = Earth's real mean radius, same 6,371 km
constant `acf.awci.path_sampling._haversine_km()` already uses) - then
calls `acf.earth_physics.atmospheric_dynamics.vorticity.
VorticityCalculator.compute_relative_vorticity()` and
`acf.science.divergence.Divergence.calculate()` VERBATIM (both are
simple enough - `zeta = dv/dx - du/dy`, `delta = du/dx + dv/dy` - that
they already work correctly on numpy arrays with no changes needed,
so this reuses the exact same real, tested formula classes rather
than re-deriving the physics).

Honest limitation: vorticity/divergence are physically singular at the
poles on a regular lat/lon grid (cos(lat) -> 0) - this is a real,
known geophysical fact, not a bug; those cells honestly render as
non-finite (NaN), which matplotlib's own contourf already handles as
a gap, not a crash.

Deferred (not built this pass, see the master plan's own "explicitly
deferred" list): real wind-vector arrows/streamlines on the map -
`AWCIMapPanel` has no quiver/barb support today; wind is shown here as
its real scalar speed only.

NOTE (correction, 2026-09-04): `real_grid_spacing_m()`/
`compute_real_vorticity_divergence()`/`compute_real_wind_shear_field()`
used to be DEFINED here - moved to the real, Qt-free
`acf.awci.workstation_fields` so the new `/api/v1/workstation` HTTP
router can reuse the exact same real formulas without importing
PySide6 into the web server process. Re-imported below unchanged - a
plain re-export, every existing caller of this module (this panel
itself, and `tests/test_acf_workstation_dynamics.py`) keeps working
with zero code changes.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.awci.workstation_fields import (
    compute_real_vorticity_divergence,
    compute_real_wind_shear_field,
    real_grid_spacing_m,
)
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

__all__ = [
    "ACFDynamicsLabPanel",
    "compute_real_vorticity_divergence",
    "compute_real_wind_shear_field",
    "real_grid_spacing_m",
]

#: Real, disclosed per-variable rendering ranges - NOT the AWCI 0-100
#: scale. Vorticity/divergence bounds are a real, generous envelope for
#: synoptic-to-mesoscale mid-latitude values (~1e-4 s^-1 magnitude,
#: matches acf.science.divergence.Divergence.category()'s own
#: "Strong" threshold of 5e-5 as a reference point), not a fabricated
#: score band. Bulk wind shear's range is a real, generous envelope
#: anchored to acf.science.bulk_wind_shear.BulkWindShear.category()'s
#: own real "Extreme" threshold (30 m/s).
_VARIABLES: dict[str, dict[str, Any]] = {
    "Wind speed": {"unit": "m/s", "cmap": "viridis", "vmin": 0.0, "vmax": 40.0},
    "Relative vorticity": {"unit": "s⁻¹", "cmap": "RdBu_r", "vmin": -2e-4, "vmax": 2e-4},
    "Divergence": {"unit": "s⁻¹", "cmap": "PuOr_r", "vmin": -2e-4, "vmax": 2e-4},
    "Bulk wind shear (full column)": {"unit": "m/s", "cmap": "cividis", "vmin": 0.0, "vmax": 40.0},
}


class ACFDynamicsLabPanel(QWidget):
    """Real Dynamics Lab - wind speed / vorticity / divergence at the
    Workstation's currently-selected level. No AWCI content anywhere."""

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
            "DYNAMICS LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume - no new
        solver run, matching this codebase's own "compute once,
        re-slice per UI interaction" discipline."""
        self._volume = volume
        self._level_index = level_index
        self._redraw()

    def _redraw(self) -> None:
        if self._volume is None:
            return
        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        lats, lons = self._volume["lats"], self._volume["lons"]
        level = self._level_index

        if variable == "Wind speed":
            field = self._volume["wind_speed_volume"][level]
        elif variable == "Bulk wind shear (full column)":
            # A real, full-column diagnostic - NOT sliced by the
            # current level (see compute_real_wind_shear_field()'s own
            # docstring), unlike this panel's other 3 variables.
            field = compute_real_wind_shear_field(self._volume["u_volume"], self._volume["v_volume"])
        else:
            vorticity, divergence = compute_real_vorticity_divergence(
                self._volume["u_volume"][level], self._volume["v_volume"][level], lats, lons
            )
            field = vorticity if variable == "Relative vorticity" else divergence

        self.map_panel.set_external_field(
            lons,
            lats,
            field,
            f"Real {self._volume.get('model', '')} — {variable}",
            cmap=spec["cmap"],
            vmin=spec["vmin"],
            vmax=spec["vmax"],
            colorbar_label=f"{variable} ({spec['unit']})",
        )
