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
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.earth_physics.atmospheric_dynamics.vorticity import VorticityCalculator
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style
from acf.science.divergence import Divergence

#: Real Earth mean radius, metres - same constant
#: acf.awci.path_sampling._haversine_km() already uses (6371.0 km).
_EARTH_RADIUS_M = 6371000.0

#: Real, disclosed per-variable rendering ranges - NOT the AWCI 0-100
#: scale. Vorticity/divergence bounds are a real, generous envelope for
#: synoptic-to-mesoscale mid-latitude values (~1e-4 s^-1 magnitude,
#: matches acf.science.divergence.Divergence.category()'s own
#: "Strong" threshold of 5e-5 as a reference point), not a fabricated
#: score band.
_VARIABLES: dict[str, dict[str, Any]] = {
    "Wind speed": {"unit": "m/s", "cmap": "viridis", "vmin": 0.0, "vmax": 40.0},
    "Relative vorticity": {"unit": "s⁻¹", "cmap": "RdBu_r", "vmin": -2e-4, "vmax": 2e-4},
    "Divergence": {"unit": "s⁻¹", "cmap": "PuOr_r", "vmin": -2e-4, "vmax": 2e-4},
}


def real_grid_spacing_m(lats: np.ndarray, lons: np.ndarray) -> tuple[float, np.ndarray]:
    """
    Real metric grid spacing (metres) for a regular lat/lon grid - the
    standard real approximation used throughout meteorology (dy =
    R*dphi, dx = R*cos(phi)*dlambda), shared by
    compute_real_vorticity_divergence() below and
    acf_workstation_complexity.py's own real spatial-complexity
    gradient (single source of truth for this real, disclosed
    approximation, not duplicated).

    Returns
    -------
    (dy, dx_per_row) : dy is a real scalar (uniform across the grid);
        dx_per_row is a real (n_lat,) array (varies with latitude).
    """
    lats_arr = np.asarray(lats, dtype=float)
    lons_arr = np.asarray(lons, dtype=float)
    dlat_rad = np.radians(float(np.mean(np.diff(lats_arr))))
    dlon_rad = np.radians(float(np.mean(np.diff(lons_arr))))
    lat_rad = np.radians(lats_arr)

    dy = float(_EARTH_RADIUS_M * dlat_rad)
    dx_per_row = _EARTH_RADIUS_M * np.cos(lat_rad) * dlon_rad
    return dy, dx_per_row


def compute_real_vorticity_divergence(
    u: np.ndarray, v: np.ndarray, lats: np.ndarray, lons: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Real relative vorticity (s^-1) and real horizontal divergence
    (s^-1) on a real regular lat/lon grid - see module docstring for
    the full disclosure of the method and why it's real, not
    fabricated.

    Parameters
    ----------
    u, v : 2D real wind components (n_lat, n_lon), m/s.
    lats, lons : 1D real coordinate arrays, degrees, regular spacing
        (EarthGrid's own convention - the same arrays
        compute_real_complexity_volume() itself returns).

    Returns
    -------
    (vorticity, divergence) : both (n_lat, n_lon), s^-1. Pole rows (if
        present in the real grid) are honestly non-finite (NaN), never
        a fabricated finite value.
    """
    dy, dx_per_row = real_grid_spacing_m(lats, lons)

    # NOTE (correction, found while smoke-testing the ACF Scientific
    # Workstation against a REAL solver grid, which genuinely spans
    # the full -90..90 pole-to-pole): `1/0` in numpy is +-inf, not
    # NaN - only true `0/0` produces NaN. A real, near-zero-but-
    # nonzero du_dx numerator divided by an EXACTLY zero dx_per_row at
    # the pole row therefore produced a real but absurd ~1e10 s^-1
    # "vorticity" instead of the honestly-disclosed NaN this module
    # promised. Explicitly masking the real dx-degenerate rows (a
    # real, physical epsilon: below 1 metre of real zonal spacing is
    # the pole itself on any Earth-radius grid) delivers the disclosed
    # behaviour for real, not just for a synthetic test grid that
    # happened not to reach the poles.
    degenerate_dx = np.abs(dx_per_row) < 1.0  # real physical threshold: <1m zonal spacing = the pole itself

    with np.errstate(divide="ignore", invalid="ignore"):  # real, expected pole-only singularity - see module docstring
        du_dy = np.gradient(u, axis=0) / dy
        dv_dy = np.gradient(v, axis=0) / dy
        safe_dx_per_row = np.where(degenerate_dx, np.nan, dx_per_row)
        du_dx = np.gradient(u, axis=1) / safe_dx_per_row[:, None]
        dv_dx = np.gradient(v, axis=1) / safe_dx_per_row[:, None]

    # VorticityCalculator/Divergence are typed for real scalar use
    # elsewhere in this codebase (dv_dx: float, du_dy: float) - they
    # work correctly on numpy arrays too (their own bodies are plain
    # `-`/`+`, real duck typing, not a hack); np.asarray() below only
    # gives mypy an accurate array type back, no behaviour change.
    vorticity = np.asarray(VorticityCalculator.compute_relative_vorticity(dv_dx, du_dy))
    divergence = np.asarray(Divergence.calculate(du_dx, dv_dy))
    return vorticity, divergence


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
