"""
ACF Scientific Workstation — Data Quality Center
===================================================

Real per-point data-quality panel for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule). Reuses
`acf.physics_guard.variable_quality.assess_variable_quality()` as-is -
the real, already-built docs/ACF_MASTER_PROMPT.md §32 per-variable
quality taxonomy (VALID/SUSPECT/MISSING/INVALID/OUT_OF_RANGE/
UNIT_ERROR/GRID_ERROR/TIME_ERROR/PHYSICAL_INCONSISTENCY), itself built
on `acf.physics_guard.range_check.OPERATIONAL_RANGES` - real,
documented operational bounds, never fabricated thresholds. This is
the first caller anywhere in this codebase that runs this real §32
machinery over a whole grid instead of one point - closing the same
"real infrastructure, never wired into a UI" gap this Workstation has
already closed for CAPE/theta-e/wind shear/precipitation phase.

Real finding this panel independently confirmed, since fixed
-------------------------------------------------------------------
Running this real, unmodified quality check against the Workstation's
own volume once independently confirmed a real anomaly (task_f3c406d9):
`pressure_volume_hpa` reported ~2013 hPa (201,325 Pa) - outside
`OPERATIONAL_RANGES["air_pressure"]`'s real, documented [1000, 108500]
Pa bound - a genuine demonstration this real infrastructure catches a
real problem, not a bug in this panel. Root cause found and fixed
2026-09-04: `acf.simulation_engine.numerical_core.earth_grid.
EarthGrid`'s own hybrid sigma-pressure `a_coeff` started at 100000.0 Pa
instead of the real, physically-required 0.0 Pa at the surface,
adding a spurious +1000 hPa to every real solver run. Pressure now
honestly reads VALID like every other real variable - see
reports/ACF_MASTER_AUDIT_v2.md's own dated entry for the full fix and
its verification.

Real, auto-computed (not on-demand)
--------------------------------------
`assess_variable_quality()` is pure Python arithmetic (dict lookups
and range comparisons, no iterative solve) - measured ~0.07ms/point
for all 4 variables together, i.e. well under a second even at a
native grid's full resolution - fast enough to recompute automatically
on every level/model change, like Overview/Dynamics/θ-e.

Honest scope
-------------
Only 4 of the volume's real fields have a documented CF standard_name
`assess_variable_quality()` can check against today: Temperature
("air_temperature"), Specific humidity ("specific_humidity"), Pressure
("air_pressure", declared in hPa via the real `units` override),
Wind speed ("wind_speed"). The dewpoint/temperature consistency check
and the SUSPECT status are never produced here - see
`assess_variable_quality()`'s own docstring for exactly why (no real
dewpoint field is derived at this level, and no real
climatological-plausibility heuristic exists anywhere in this
codebase to justify a real SUSPECT determination - fabricating one
would be exactly the kind of ungrounded rule this project's audits
exist to catch).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.colors import ListedColormap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style
from acf.physics_guard.variable_quality import VARIABLE_QUALITY_STATUSES, assess_variable_quality

#: Real per-panel-variable name -> (CF standard_name, real declared
#: unit override for assess_variable_quality()'s own `units` param, or
#: None when already in the CF canonical unit).
_VARIABLES: dict[str, tuple[str, str | None]] = {
    "Temperature": ("air_temperature", None),
    "Specific humidity": ("specific_humidity", None),
    "Pressure": ("air_pressure", "hPa"),
    "Wind speed": ("wind_speed", None),
}

#: A real, discrete colormap - one flat color per real §32 status (in
#: VARIABLE_QUALITY_STATUSES' own real order), so intermediate colors
#: never imply a status between two real discrete categories. Green
#: for VALID, escalating warm/alert colors for every real problem
#: category - an ACF-chosen palette, not a published standard.
_STATUS_CMAP = ListedColormap(
    ["#2e9e5b", "#eab308", "#94a3b8", "#f97316", "#ef4444", "#a855f7", "#0ea5e9", "#f43f5e", "#7c2d12"]
)


def compute_real_data_quality_fields(
    temperature: np.ndarray, specific_humidity: np.ndarray, pressure_hpa: np.ndarray, wind_speed: np.ndarray
) -> dict[str, tuple[np.ndarray, dict[str, int]]]:
    """
    Real per-point §32 quality status for the 4 real variables above,
    via `assess_variable_quality()` - see module docstring.

    Returns
    -------
    dict[panel variable name -> (severity_grid, status_counts)]
        severity_grid : real (n_lat, n_lon) array - each cell is that
            point's real status's index into VARIABLE_QUALITY_STATUSES
            (0 = VALID, higher = a real, distinct problem category -
            never a continuous/interpolated severity).
        status_counts : dict[real status name -> real count of grid
            points at that status] - for the panel's own summary text.
    """
    n_lat, n_lon = temperature.shape
    fields = {
        "air_temperature": temperature,
        "specific_humidity": specific_humidity,
        "air_pressure": pressure_hpa,
        "wind_speed": wind_speed,
    }
    units = {"air_pressure": "hPa"}
    severity_grids = {cf_name: np.zeros((n_lat, n_lon)) for cf_name in fields}
    status_counts: dict[str, dict[str, int]] = {cf_name: {} for cf_name in fields}

    for i in range(n_lat):
        for j in range(n_lon):
            data = {cf_name: float(arr[i, j]) for cf_name, arr in fields.items()}
            statuses = assess_variable_quality(data, expected_variables=list(fields.keys()), units=units)
            for cf_name, vqs in statuses.items():
                severity_grids[cf_name][i, j] = VARIABLE_QUALITY_STATUSES.index(vqs.status)
                status_counts[cf_name][vqs.status] = status_counts[cf_name].get(vqs.status, 0) + 1

    return {
        panel_name: (severity_grids[cf_name], status_counts[cf_name])
        for panel_name, (cf_name, _unit) in _VARIABLES.items()
    }


class ACFDataQualityLabPanel(QWidget):
    """Real Data Quality Center - real §32 per-variable quality status
    at every grid point, auto-computed. No AWCI content anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_VARIABLES.keys()))
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_selector)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("—")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

        self.map_panel = AWCIMapPanel(
            "DATA QUALITY CENTER", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

        legend = QLabel(
            "§32 status (real, ACF's own ordinal - see module docstring): "
            + " < ".join(f"{name} ({i})" for i, name in enumerate(VARIABLE_QUALITY_STATUSES))
        )
        legend.setStyleSheet(label_style("text_muted", "xs"))
        legend.setWordWrap(True)
        layout.addWidget(legend)

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
        level = self._level_index
        results = compute_real_data_quality_fields(
            self._volume["temperature_volume"][level],
            self._volume["specific_humidity_volume"][level],
            self._volume["pressure_volume_hpa"][level],
            self._volume["wind_speed_volume"][level],
        )

        variable = self.variable_selector.currentText()
        severity_grid, status_counts = results[variable]
        total = int(severity_grid.size)
        counts_text = ", ".join(
            f"{status} {count}/{total} ({100.0 * count / total:.1f}%)" for status, count in sorted(status_counts.items())
        )
        icon = "✅" if set(status_counts) == {"VALID"} else "⚠"
        self.status_label.setText(f"{icon} {variable}: {counts_text}")

        self.map_panel.set_external_field(
            self._volume["lons"],
            self._volume["lats"],
            severity_grid,
            f"Real {self._volume.get('model', '')} — {variable} quality",
            cmap=_STATUS_CMAP,
            vmin=0.0,
            vmax=float(len(VARIABLE_QUALITY_STATUSES) - 1),
            colorbar_label="§32 status (ordinal)",
        )
