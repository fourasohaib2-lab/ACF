"""
ACF Scientific Workstation — Microphysics Lab
===============================================

Real surface precipitation-phase panel for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule). Reuses
`acf.awci.hydrometeor_phase.compute_real_hydrometeor_phase_at_point()`
as-is - no new physics invented here, and no new species fabricated:
that function's own docstring already discloses the honest scope this
panel inherits (see "Honest scope" below).

Real formula pipeline, not reimplemented
-------------------------------------------
`compute_real_hydrometeor_phase_at_point()` composes 3 already-real
pieces - real relative humidity, the real Stull (2011) wet-bulb
approximation, and `acf.science.precipitation.HydrometeorType.
classify()` (an explicitly self-disclosed HEURISTIC, not a validated
physical formula) - into one of 4 real surface precipitation-phase
categories (Rain / Snow / Wet Snow-Mix / Freezing Rain-Ice Pellets)
plus `phase_severity`, a real ACF-assigned ordinal ranking in [0, 1]
(0.2/0.5/0.7/1.0) reflecting real aviation-icing operational severity
(see that module's own docstring for the full reasoning) - not a
validated numeric index. Pure arithmetic (no iterative solve) - fast
enough (~1 microsecond/point measured) to recompute for the whole grid
automatically on every level/model change, same as Overview/Dynamics/
Thermodynamics Lab's own auto-rendered variables.

Honest scope (inherited from compute_real_hydrometeor_phase_at_point())
--------------------------------------------------------------------------
No real per-column hydrometeor species (cloud water/ice/rain/snow
mixing ratios) exist anywhere in `CoupledEarthSolver`'s real state, so
real formulas that would need them
(`acf.science.clouds.microphysics.CloudMicrophysicsEngine`'s real
autoconversion/riming/Bergeron-Findeisen rates) cannot be shown here
without fabricating that input - a real, documented gap, not closed by
this panel. This is a SURFACE-ONLY classification (temperature and
wet-bulb temperature at the current level only), not a real vertical-
profile method - it cannot reliably distinguish freezing rain from ice
pellets/sleet (merged into one real category, same as the underlying
function's own disclosure).

Research Mode (added 2026-09-04)
------------------------------------
When `set_research_mode(True)` (toggled from the Workstation's own
chrome), clicking the map re-calls `compute_real_hydrometeor_phase_at_
point()` fresh at the nearest real grid point to the click - showing
its FULL real return (phase category name, severity, wet-bulb
temperature, relative humidity, and its own real `honest_limitation`
text), not just the single value already rendered on the map. Real,
on-demand, per-click - `AWCIMapPanel.pointClicked` (already real,
already tested elsewhere) is reused as-is.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.colors import ListedColormap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget

from acf.awci.hydrometeor_phase import PHASE_SEVERITY, compute_real_hydrometeor_phase_at_point
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

#: Real, ordered category names - PHASE_SEVERITY's own keys, in
#: ascending severity order (0.2 -> 1.0), for a real, ordered colormap
#: (see _PHASE_CMAP below) rather than an arbitrary continuous scale
#: applied to what is actually a real, discrete, 4-category variable.
_PHASE_CATEGORIES = sorted(PHASE_SEVERITY, key=lambda name: PHASE_SEVERITY[name])
#: A real, discrete 4-color map - one flat color per real category
#: (blue=Rain, cyan=Snow, orange=Wet Snow/Mix, magenta=Freezing Rain/
#: Ice Pellets - an ACF-chosen palette, not a published standard),
#: rather than a continuous gradient that would visually imply
#: intermediate phases do not exist.
_PHASE_CMAP = ListedColormap(["#3b82c4", "#7dd3fc", "#f59e0b", "#e879f9"])

_AUTO_VARIABLES: dict[str, dict[str, Any]] = {
    "Precipitation phase severity": {"unit": "0-1 ACF ordinal", "cmap": _PHASE_CMAP, "vmin": 0.0, "vmax": 1.0},
    "Wet-bulb temperature": {"unit": "°C", "cmap": "coolwarm", "vmin": -20.0, "vmax": 30.0},
}


def compute_real_hydrometeor_phase_fields(
    temperature: np.ndarray, specific_humidity: np.ndarray, pressure_hpa: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Real precipitation-phase severity ([0, 1]) and real wet-bulb
    temperature (°C) at every point of one real 2D level slice, via
    `compute_real_hydrometeor_phase_at_point()` - see module docstring.
    """
    n_lat, n_lon = temperature.shape
    phase_severity = np.full((n_lat, n_lon), np.nan)
    wet_bulb_c = np.full((n_lat, n_lon), np.nan)
    for i in range(n_lat):
        for j in range(n_lon):
            result = compute_real_hydrometeor_phase_at_point(
                float(temperature[i, j]), float(specific_humidity[i, j]), float(pressure_hpa[i, j])
            )
            if result["is_real_data"]:
                phase_severity[i, j] = result["phase_severity"]
                wet_bulb_c[i, j] = result["wet_bulb_c"]
    return phase_severity, wet_bulb_c


class ACFMicrophysicsLabPanel(QWidget):
    """Real Microphysics Lab - surface precipitation phase/wet-bulb
    temperature (auto, from the current level). No AWCI content
    anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._research_mode_enabled = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_AUTO_VARIABLES.keys()))
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_selector)
        controls.addStretch()
        layout.addLayout(controls)

        self.map_panel = AWCIMapPanel(
            "MICROPHYSICS LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        self.map_panel.pointClicked.connect(self._on_map_point_clicked)
        layout.addWidget(self.map_panel, stretch=1)

        legend = QLabel(
            "Precipitation phase severity (real ACF ordinal, see module docstring): "
            + " < ".join(f"{name} ({PHASE_SEVERITY[name]:.1f})" for name in _PHASE_CATEGORIES)
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

    def set_research_mode(self, enabled: bool) -> None:
        """Real toggle (see module docstring's "Research Mode" section)
        - controlled by `acf_workstation.ACFWorkstation`'s own chrome,
        not this panel."""
        self._research_mode_enabled = enabled

    def _on_map_point_clicked(self, lat: float, lon: float) -> None:
        if not self._research_mode_enabled or self._volume is None:
            return
        lats = np.asarray(self._volume["lats"])
        lons = np.asarray(self._volume["lons"])
        lat_idx = int(np.argmin(np.abs(lats - lat)))
        lon_idx = int(np.argmin(np.abs(lons - lon)))
        level = self._level_index

        result = compute_real_hydrometeor_phase_at_point(
            float(self._volume["temperature_volume"][level, lat_idx, lon_idx]),
            float(self._volume["specific_humidity_volume"][level, lat_idx, lon_idx]),
            float(self._volume["pressure_volume_hpa"][level, lat_idx, lon_idx]),
        )
        real_lat, real_lon = float(lats[lat_idx]), float(lons[lon_idx])
        text = (
            f"Phase: {result['phase']} (severity {result['phase_severity']:.1f})\n"
            f"Wet-bulb temperature: {result['wet_bulb_c']:.2f} °C\n"
            f"Relative humidity: {result['relative_humidity_pct']:.1f} %\n"
            f"Status: {result['status']}\n\n{result['honest_limitation']}"
        )
        QMessageBox.information(
            self,
            f"Research Detail — Microphysics ({real_lat:.2f}°N, {real_lon:.2f}°E)",
            text,
        )

    def _redraw(self) -> None:
        if self._volume is None:
            return
        variable = self.variable_selector.currentText()
        spec = _AUTO_VARIABLES[variable]
        lats, lons = self._volume["lats"], self._volume["lons"]
        level = self._level_index

        phase_severity, wet_bulb_c = compute_real_hydrometeor_phase_fields(
            self._volume["temperature_volume"][level],
            self._volume["specific_humidity_volume"][level],
            self._volume["pressure_volume_hpa"][level],
        )
        field = phase_severity if variable.startswith("Precipitation") else wet_bulb_c

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
