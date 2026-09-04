"""
ACF Scientific Workstation — Atmospheric Interaction Graph
================================================================

Real, always-visible per-level correlation network (Phase 34,
2026-09-05, matching the reference mockup's own persistent right-
column "ATMOSPHERIC INTERACTION GRAPH" box - `docs/reference/
acf_scientific_workstation_reference.jpg`).

Real formula, reused as-is - not reimplemented
---------------------------------------------------
Every edge is the real, standard Pearson correlation coefficient
between two real gridded fields at the current level, via
`acf_workstation_interactions.compute_real_local_interaction()` - the
SAME statistically-justified function the Interaction Engine tab
already uses (see that module's own docstring for the full derivation
and the master-spec rule it satisfies: never an arbitrary `A x B`
product). This widget only chooses which 5 real variables to always
correlate and draws the result as a small network, it computes
nothing new.

Real, honest node choice
----------------------------
Five real, cheap, always-available gridded fields at the current
level - Wind (wind_speed_volume), Terrain (`acf.awci.terrain_elevation.
interpolate_real_terrain_elevation()`, level-independent, the same
real bundled SRTM15+ grid Terrain Lab already uses), Humidity (real
relative humidity, `compute_real_theta_e_and_rh_fields()`, already
reused by Thermodynamics Lab), Temperature (temperature_volume), and
Precipitation (real precipitation-phase severity,
`compute_real_hydrometeor_phase_fields()`, already reused by
Microphysics Lab). Honest disclosure: the mockup's own 5th label is
"Convection", not "Temperature" - no real, cheap, always-available
gridded convection field exists in this Workstation today (CAPE/CIN is
only computed on-demand, per-point, in Thermodynamics Lab's own
Research Mode) - Temperature substitutes for it here rather than
fabricating a convection proxy.
"""

from __future__ import annotations

import math
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.awci.terrain_elevation import interpolate_real_terrain_elevation
from acf.awci.workstation_fields import compute_real_theta_e_and_rh_fields
from acf.gui.dashboard.acf_workstation_interactions import compute_real_local_interaction
from acf.gui.dashboard.acf_workstation_microphysics import compute_real_hydrometeor_phase_fields
from acf.gui.theme_tokens import TOKENS

#: Real, fixed node set - see module docstring's "Real, honest node choice".
NODES: tuple[str, ...] = ("Wind", "Terrain", "Humidity", "Temperature", "Precipitation")


class ACFInteractionGraphWidget(QWidget):
    """Real 5-node Pearson-correlation network at the current level -
    see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._edges: dict[tuple[str, str], float] = {}
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.text(
            0.5, 0.5, "No real volume yet", transform=self.axis.transAxes,
            ha="center", va="center", color=TOKENS.text_muted, fontsize=8,
        )
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_title("ATMOSPHERIC INTERACTION GRAPH", color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.canvas.draw_idle()

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real, per-level recompute - cheap (~50ms at AROME's own full
        90x180 grid, measured) - no new solver run, matching this
        Workstation's own "compute once, re-slice per interaction"
        discipline; only the 5 real correlation values below are
        genuinely re-derived per level."""
        lats, lons = volume["lats"], volume["lons"]
        wind = volume["wind_speed_volume"][level_index]
        temperature = volume["temperature_volume"][level_index]
        specific_humidity = volume["specific_humidity_volume"][level_index]
        pressure_hpa = volume["pressure_volume_hpa"][level_index]

        terrain = interpolate_real_terrain_elevation(lats, lons)
        _theta_e, relative_humidity = compute_real_theta_e_and_rh_fields(temperature, specific_humidity, pressure_hpa)
        phase_severity, _wet_bulb_c = compute_real_hydrometeor_phase_fields(temperature, specific_humidity, pressure_hpa)

        fields: dict[str, np.ndarray] = {
            "Wind": wind,
            "Terrain": terrain,
            "Humidity": relative_humidity,
            "Temperature": temperature,
            "Precipitation": phase_severity,
        }
        self._edges = {}
        for i, a in enumerate(NODES):
            for b in NODES[i + 1 :]:
                _local, pearson_r = compute_real_local_interaction(fields[a], fields[b])
                self._edges[(a, b)] = pearson_r
        self._draw()

    def _draw(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.set_xlim(-1.4, 1.4)
        self.axis.set_ylim(-1.4, 1.4)
        self.axis.set_aspect("equal")
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        for spine in self.axis.spines.values():
            spine.set_visible(False)

        n = len(NODES)
        positions = {
            name: (math.cos(2 * math.pi * i / n + math.pi / 2), math.sin(2 * math.pi * i / n + math.pi / 2))
            for i, name in enumerate(NODES)
        }

        for (a, b), r in self._edges.items():
            xa, ya = positions[a]
            xb, yb = positions[b]
            if math.isnan(r):
                self.axis.plot([xa, xb], [ya, yb], color=TOKENS.border, linewidth=0.6, linestyle=":", alpha=0.4, zorder=1)
                continue
            color = TOKENS.warning if r >= 0 else TOKENS.accent_primary
            self.axis.plot(
                [xa, xb], [ya, yb], color=color,
                linewidth=0.5 + 3.0 * abs(r), alpha=0.25 + 0.65 * abs(r), zorder=1,
            )

        for name, (x, y) in positions.items():
            self.axis.scatter([x], [y], s=220, color=TOKENS.bg_surface, edgecolors=TOKENS.accent_primary, linewidths=1.4, zorder=2)
            self.axis.annotate(
                name, (x, y), ha="center", va="center", color=TOKENS.text_primary, fontsize=7, fontweight="bold", zorder=3,
            )

        self.axis.set_title("ATMOSPHERIC INTERACTION GRAPH", color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.02)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"has_edges": bool(self._edges), "edges": dict(self._edges)}
