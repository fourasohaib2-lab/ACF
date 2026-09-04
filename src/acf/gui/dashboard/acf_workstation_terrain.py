"""
ACF Scientific Workstation — Terrain Lab
==========================================

Real orographic panel for `acf_workstation.ACFWorkstation` (see that
module's own docstring for the Workstation's overall "ACF CORE ONLY -
NO AWCI" rule) - the last remaining planned §8 spec module, built
2026-09-04 after the user explicitly authorized downloading a real,
small, cited external elevation dataset (see `acf.awci.
terrain_elevation`'s own module docstring for the exact source/
license/citation).

Why this Lab was blocked, and how it was unblocked
-------------------------------------------------------
`acf.awci.orographic_froude`'s own module docstring named the exact
real blocker: "CoupledEarthSolver's real state has no terrain-
elevation field at all" - a real, cited mountain-wave Froude number
formula (`compute_real_mountain_wave_froude_number_at_point()`, ICAO
Doc 9817; AMS Aviation Meteorology) already existed, genuinely unable
to run for lack of real input data. `acf.awci.terrain_elevation`
supplies that real input (a real, bundled, ~111 KB SRTM15+ V2.7 1
arc-degree grid, GMT's own official public data server) - see
`acf.awci.workstation_fields.compute_real_terrain_field()`'s own
docstring for the full real pipeline (real terrain elevation, real
near-surface Brunt-Väisälä static stability, real mountain-wave Froude
number) and its honest, disclosed simplifications.

Real, cheap, auto-rendered - not on-demand
-------------------------------------------------------
Unlike CAPE/CIN's real MetPy parcel ascent (~5ms/point, needing an
on-demand button + off-thread worker + a coarser-grid stride),
`compute_real_terrain_field()` is fully vectorized (simple, real,
closed-form algebraic formulas - see that function's own docstring) -
verified empirically at this Workstation's own largest real grid
(AROME, 90x180=16200 points) to run in well under a second. This Lab
therefore auto-renders on `update_from_volume()`, same real
"compute once, re-slice/recompute per UI interaction" convention as
Overview/Dynamics Lab, never a second solver run.

Terrain elevation/static stability are real, full-column-independent
diagnostics (elevation never changes with level; static stability here
is deliberately a near-surface estimate, see that function's own
docstring) - `update_from_volume()`'s `level_index` is accepted for
this panel's own bookkeeping consistency but not used to re-slice
anything, same "level-independent" convention already established for
Dynamics Lab's own "Bulk wind shear (full column)" variable.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.awci.workstation_fields import compute_real_terrain_field
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

#: Real, disclosed rendering choices. Elevation's range is a real,
#: generous envelope covering Earth's real extremes (Mariana Trench to
#: Everest, comfortably). Static stability's range is a real, generous
#: envelope for tropospheric N (typically ~0.01-0.02 rad/s - Holton &
#: Hakim). Froude's range (0-5) brackets the real regime split this
#: formula is defined by (Fr < 1 flow-blocking/stationary-wave hazard,
#: Fr > 1 smoother flow - see `compute_real_mountain_wave_froude_
#: number_at_point()`'s own docstring), never a fabricated score band.
_VARIABLES: dict[str, dict[str, Any]] = {
    "Terrain elevation": {
        "key": "elevation_m", "unit": "m", "cmap": "terrain", "vmin": -8000.0, "vmax": 8000.0,
    },
    "Static stability (Brunt-Väisälä N)": {
        "key": "brunt_vaisala_n_s1", "unit": "rad/s", "cmap": "viridis", "vmin": 0.0, "vmax": 0.05,
    },
    "Mountain-wave Froude number": {
        "key": "froude_number", "unit": "dimensionless", "cmap": "RdYlBu", "vmin": 0.0, "vmax": 5.0,
    },
}


class ACFTerrainLabPanel(QWidget):
    """Real Terrain Lab - terrain elevation, near-surface static
    stability, and mountain-wave Froude number. No AWCI content, no
    single fabricated score anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._result: dict[str, Any] | None = None

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

        self.map_panel = AWCIMapPanel(
            "TERRAIN LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

        legend = QLabel(
            "Real, cited SRTM15+ V2.7 terrain elevation (Tozer et al., 2019) and a real mountain-wave "
            "Froude number Fr = U/(N·H) (ICAO Doc 9817) - Fr < 1 favors flow blocking/stationary orographic "
            "waves, Fr > 1 smoother flow over terrain (see acf.awci.orographic_froude's own docstring)."
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
        """Real, cheap, synchronous recompute (see module docstring for
        why this doesn't need an on-demand/off-thread worker) - never a
        second solver run."""
        self._volume = volume
        self._level_index = level_index
        if volume is not None:
            self._result = compute_real_terrain_field(
                volume["temperature_volume"], volume["pressure_volume_hpa"], volume["wind_speed_volume"],
                volume["lats"], volume["lons"],
            )
        self._redraw()

    def _redraw(self) -> None:
        if self._result is None:
            return
        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        field = self._result[spec["key"]]

        self.map_panel.set_external_field(
            list(self._result["lons"]),
            list(self._result["lats"]),
            field,
            f"Real {self._volume.get('model', '') if self._volume else ''} — {variable}",
            cmap=spec["cmap"],
            vmin=spec["vmin"],
            vmax=spec["vmax"],
            colorbar_label=f"{variable} ({spec['unit']})",
        )
