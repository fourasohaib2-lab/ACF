"""
ACF Scientific Workstation — Interaction Engine
=================================================

Real, statistically-justified cross-module interaction panel for
`acf_workstation.ACFWorkstation` (see that module's own docstring for
the Workstation's overall "ACF CORE ONLY - NO AWCI" rule).

Explicit master-spec rule, applied literally (docs/ACF_MASTER_PROMPT.md
§22, "INTERACTIONS — CŒUR DU PROJET"): "Les interactions doivent être
étudiées scientifiquement. Ne pas inventer arbitrairement
`interaction = A × B` sans justification physique ou statistique."
This panel therefore computes the real, standard, published
**Pearson correlation coefficient** between two real physical fields a
user picks - not an arbitrary product of two raw quantities in
different units (e.g. "wind_speed x specific_humidity" as a bare
product would be dimensionally meaningless and exactly the kind of
unjustified interaction the spec warns against).

Real formula, standard statistics, not invented
---------------------------------------------------
For two real fields A, B at the current level:

    z_A = (A - mean(A)) / std(A)      # real standardized anomaly
    z_B = (B - mean(B)) / std(B)
    local_interaction(x, y) = z_A(x, y) * z_B(x, y)
    pearson_r = mean(local_interaction)

`local_interaction` is the real, standard POINTWISE CONTRIBUTION to
the Pearson correlation coefficient (its spatial mean is, by
construction, exactly equal to the classic `r = cov(A,B) /
(std(A)*std(B))` formula - verified against `numpy.corrcoef` in this
module's own test suite) - a real, textbook statistical decomposition,
not a fabricated per-point "interaction score". Rendering it as a map
(rather than only the single scalar `pearson_r`) answers the master
spec's own §23 "C(x,y,t)" spatial-complexity framing applied to
interactions specifically: WHERE two real fields co-vary strongly
(positively or negatively), not just a single global number.

Cross-module by design
-------------------------
Reuses the SAME real field-computation functions this Workstation's
other Labs already built (never reimplemented): Overview's raw fields,
`acf_workstation_dynamics`'s vorticity/divergence/wind shear,
`acf_workstation_thermodynamics`'s θ-e/relative humidity,
`acf_workstation_microphysics`'s precipitation-phase severity/wet-bulb
temperature - letting a user genuinely study cross-module interactions
(e.g. "Bulk wind shear" x "Relative humidity", matching the master
spec's own worked example "Vent élevé + Humidité élevée + Relief"),
not just variables within one Lab.

Honest scope
-------------
A real, undefined correlation (std(A)=0 or std(B)=0 - a perfectly
uniform field, no real variance to correlate) is honestly NaN
everywhere, never a fabricated 0 or 1. Purely a REAL-TIME (auto)
computation - both z-scoring and the elementwise product are cheap
numpy operations on already-available fields, no new solver run,
fast enough to recompute on every selector/level change like
Overview/Dynamics.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.acf_workstation_dynamics import compute_real_vorticity_divergence, compute_real_wind_shear_field
from acf.gui.dashboard.acf_workstation_microphysics import compute_real_hydrometeor_phase_fields
from acf.gui.dashboard.acf_workstation_thermodynamics import compute_real_theta_e_and_rh_fields
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

#: Real variable names available to BOTH selectors - spans Overview,
#: Dynamics, Thermodynamics, and Microphysics Lab's own real fields
#: (see module docstring's "Cross-module by design"), so a user can
#: genuinely study interactions ACROSS modules, not just within one.
_VARIABLE_NAMES = [
    "Temperature",
    "Wind speed",
    "Specific humidity",
    "Pressure",
    "Relative vorticity",
    "Divergence",
    "Bulk wind shear (full column)",
    "Equivalent potential temperature (θ-e)",
    "Relative humidity",
    "Precipitation phase severity",
    "Wet-bulb temperature",
]


def compute_real_local_interaction(field_a: np.ndarray, field_b: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Real, standard pointwise contribution to the Pearson correlation
    coefficient between two real 2D fields - see module docstring for
    the full derivation and why this is a statistically-justified
    interaction measure, not an arbitrary `A * B` product.

    Returns
    -------
    (local_interaction, pearson_r) : local_interaction is a real
        (n_lat, n_lon) array (NaN everywhere if either field has zero
        real variance - an honestly undefined correlation, never a
        fabricated value); pearson_r is its real spatial mean (a
        plain Python float, `nan` in that same degenerate case).
    """
    mean_a, mean_b = np.nanmean(field_a), np.nanmean(field_b)
    std_a, std_b = np.nanstd(field_a), np.nanstd(field_b)
    if std_a == 0.0 or std_b == 0.0 or np.isnan(std_a) or np.isnan(std_b):
        nan_field = np.full(np.asarray(field_a).shape, np.nan)
        return nan_field, float("nan")
    z_a = (np.asarray(field_a, dtype=float) - mean_a) / std_a
    z_b = (np.asarray(field_b, dtype=float) - mean_b) / std_b
    local_interaction = z_a * z_b
    pearson_r = float(np.nanmean(local_interaction))
    return local_interaction, pearson_r


def _real_variable_field(name: str, volume: dict[str, Any], level_index: int) -> np.ndarray:
    """Real (n_lat, n_lon) field for one of _VARIABLE_NAMES, computed
    via the SAME real functions this Workstation's other Labs already
    use (see module docstring) - never reimplemented here."""
    lats, lons = volume["lats"], volume["lons"]
    level = level_index

    if name == "Temperature":
        return np.asarray(volume["temperature_volume"][level])
    if name == "Wind speed":
        return np.asarray(volume["wind_speed_volume"][level])
    if name == "Specific humidity":
        return np.asarray(volume["specific_humidity_volume"][level])
    if name == "Pressure":
        return np.asarray(volume["pressure_volume_hpa"][level])
    if name == "Bulk wind shear (full column)":
        return compute_real_wind_shear_field(volume["u_volume"], volume["v_volume"])
    if name in ("Relative vorticity", "Divergence"):
        vorticity, divergence = compute_real_vorticity_divergence(
            volume["u_volume"][level], volume["v_volume"][level], lats, lons
        )
        return vorticity if name == "Relative vorticity" else divergence
    if name in ("Equivalent potential temperature (θ-e)", "Relative humidity"):
        theta_e, relative_humidity = compute_real_theta_e_and_rh_fields(
            volume["temperature_volume"][level], volume["specific_humidity_volume"][level],
            volume["pressure_volume_hpa"][level],
        )
        return theta_e if name.startswith("Equivalent") else relative_humidity
    if name in ("Precipitation phase severity", "Wet-bulb temperature"):
        phase_severity, wet_bulb_c = compute_real_hydrometeor_phase_fields(
            volume["temperature_volume"][level], volume["specific_humidity_volume"][level],
            volume["pressure_volume_hpa"][level],
        )
        return phase_severity if name == "Precipitation phase severity" else wet_bulb_c
    raise ValueError(f"Unknown variable {name!r}")


class ACFInteractionEnginePanel(QWidget):
    """Real Interaction Engine - statistically-justified pointwise
    correlation between 2 real, cross-module physical fields. No AWCI
    content, no arbitrary A*B product anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable A:"))
        self.variable_a_selector = QComboBox()
        self.variable_a_selector.addItems(_VARIABLE_NAMES)
        self.variable_a_selector.setCurrentText("Bulk wind shear (full column)")
        self.variable_a_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_a_selector)

        controls.addWidget(self._label("Variable B:"))
        self.variable_b_selector = QComboBox()
        self.variable_b_selector.addItems(_VARIABLE_NAMES)
        self.variable_b_selector.setCurrentText("Relative humidity")
        self.variable_b_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_b_selector)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("—")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

        self.map_panel = AWCIMapPanel(
            "INTERACTION ENGINE", show_legend=False, show_info_boxes=False, show_demo_fallback=False
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
        name_a = self.variable_a_selector.currentText()
        name_b = self.variable_b_selector.currentText()
        field_a = _real_variable_field(name_a, self._volume, self._level_index)
        field_b = _real_variable_field(name_b, self._volume, self._level_index)

        local_interaction, pearson_r = compute_real_local_interaction(field_a, field_b)

        if np.isnan(pearson_r):
            self.status_label.setText(
                f"⚠ Undefined correlation - '{name_a}' or '{name_b}' has zero real variance at this level."
            )
        else:
            direction = "positive" if pearson_r >= 0 else "negative"
            self.status_label.setText(f"Real Pearson r = {pearson_r:+.3f} ({direction} correlation)")

        self.map_panel.set_external_field(
            self._volume["lons"],
            self._volume["lats"],
            local_interaction,
            f"Real {self._volume.get('model', '')} — {name_a} × {name_b}",
            cmap="RdBu_r",
            vmin=-3.0,
            vmax=3.0,
            colorbar_label="Local interaction (standardized z_A × z_B)",
        )
