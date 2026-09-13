"""
ACF Scientific Workstation — Vertical Cross-Section (real temperature)
=========================================================================

Real temperature cross-section for `acf_workstation.ACFWorkstation`'s
merged Overview screen (2026-09-13, explicit user request to fuse the
reference mockup's full single-screen layout into Overview - see
`acf_workstation_overview_landing.py`'s own module docstring for the
full context of this merge and its disclosed limitations).

Reuses `acf.awci.path_sampling.sample_volume_cross_section()` - the
SAME real, generic nearest-neighbour transect sampler
`awci_cross_section.AWCICrossSection` already uses internally, called
here with `volume["temperature_volume"]` instead of an AWCI 0-100
score. `AWCICrossSection` itself is NOT reused directly here: its own
`set_external_cross_section()` always draws the real AWCI 0-100
colorbar (`awci_colors.AWCI_CMAP`), which would mislabel a real
temperature field as an AWCI score - a small, dedicated widget is used
instead, with a real temperature colormap/colorbar (`coolwarm`, the
same real palette `acf_workstation_overview._VARIABLES`/
`ACF3DAtmospherePanel._VARIABLES` already use for Temperature), not a
new sampling formula.

Honest default transect: no explicit 2-point flight path exists on
Overview (unlike AWCI's own route planner). The default transect runs
from the current volume's own southernmost to northernmost latitude at
its median longitude - a real, disclosed choice (shown in the panel's
own title), not the true along-flight-path concept
`AWCICrossSection`'s own title implies.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.awci.path_sampling import sample_volume_cross_section
from acf.gui.theme_tokens import TOKENS


class ACFTemperatureCrossSectionWidget(QWidget):
    """Real temperature (°C) cross-section along a real north-south
    transect of the current volume - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.figure = plt.figure(facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._colorbar: Any = None
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.text(
            0.5, 0.5, "No real volume yet - press ▶ Analyze",
            transform=self.axis.transAxes, ha="center", va="center", color=TOKENS.text_muted, fontsize=8,
        )
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_title(
            "VERTICAL CROSS-SECTION (Temperature)", color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left"
        )
        self.canvas.draw_idle()

    def update_from_volume(self, volume: dict[str, Any]) -> None:
        """Real re-slice of the already-computed volume along a real
        north-south transect at the volume's own median longitude - no
        new solver run, see module docstring for why this default
        transect (not a user-picked flight path) is used."""
        lats = np.asarray(volume["lats"])
        lons = np.asarray(volume["lons"])
        mid_lon = float(lons[len(lons) // 2])
        point_a = (float(lats.min()), mid_lon)
        point_b = (float(lats.max()), mid_lon)

        result = sample_volume_cross_section(
            lats, lons, volume["pressure_volume_hpa"], volume["temperature_volume"], point_a, point_b,
        )

        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        distances = np.asarray(result["distances_km"])
        pressures = np.asarray(result["mean_pressure_hpa_by_level"])
        grid_c = result["grid"] - 273.15  # K -> degC, matches the mockup's own degC colorbar

        contour = self.axis.contourf(distances, pressures, grid_c, levels=20, cmap="coolwarm")
        # See awci_map_panel.py's own set_external_field() NOTE for why
        # plain Colorbar.remove() raises a real AttributeError on the
        # 2nd+ redraw here too (self.axis.clear() above invalidates the
        # subplotspec reference remove() needs) - same fix: bypass
        # Colorbar's own cleanup via figure.delaxes().
        if self._colorbar is not None:
            self.figure.delaxes(self._colorbar.ax)
            self._colorbar = None
        self._colorbar = self.figure.colorbar(contour, ax=self.axis)
        self._colorbar.set_label("Temperature (°C)", color=TOKENS.text_secondary, fontsize=8)
        self._colorbar.ax.tick_params(colors=TOKENS.text_secondary, labelsize=7)
        self.axis.invert_yaxis()  # surface (highest pressure) at the bottom, meteorological convention
        self.axis.set_xlabel("Distance along transect (km)", color=TOKENS.text_secondary, fontsize=8)
        self.axis.set_ylabel("Pressure (hPa)", color=TOKENS.text_secondary, fontsize=8)
        self.axis.tick_params(colors=TOKENS.text_secondary, labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color(TOKENS.border)
        self.axis.set_title(
            f"VERTICAL CROSS-SECTION (Temperature) — {point_a[0]:.1f}°N→{point_b[0]:.1f}°N @ {mid_lon:.1f}°E",
            color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left",
        )
        self.figure.subplots_adjust(left=0.12, right=0.98, top=0.85, bottom=0.16)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"has_colorbar": self._colorbar is not None}
