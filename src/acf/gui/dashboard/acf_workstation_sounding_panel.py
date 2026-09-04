"""
ACF Scientific Workstation — Vertical Complexity Sounding
=============================================================

Real, always-visible per-point vertical profile panel (Phase 33,
2026-09-05, matching the reference mockup's own persistent top-right
"VERTICAL COMPLEXITY SOUNDING" box - `docs/reference/
acf_scientific_workstation_reference.jpg`).

Real data, real point, no fabricated sounding
--------------------------------------------------
Fed by `acf.awci.vertical_field.vertical_profile_at_point()` - the
same real nearest-neighbour column extraction `acf.awci.temporal_field`/
`acf.awci.archive_field` already use - at whichever real (lat, lon) the
user last clicked on ANY of this Workstation's own map panels (every
Lab panel that has one exposes its real `AWCIMapPanel.pointClicked`
signal; `ACFWorkstation` connects every one of them to this widget, see
`acf_workstation.py`'s own `_on_map_point_clicked()`). Draws the real
per-level temperature (°C) and wind speed (m/s) at that column,
pressure-inverted (surface at the bottom, meteorological convention) -
no CAPE/CIN parcel ascent, no synthetic skew-T background, nothing
this Workstation cannot back with a real number.

Honest scope
-------------
The mockup's own small colored grid beside its sounding plot (labelled
"High Shear / Stability / CIN / CAPE / Wind Shear") is NOT built here -
that would need a real per-point stability-index summary this
Workstation does not compute at every column today (only
Thermodynamics Lab's own Research Mode click computes CAPE/CIN, and
only for its own single point-of-interest, not a persistent
always-visible grid). Deferred, disclosed, not silently dropped.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.awci.vertical_field import vertical_profile_at_point
from acf.gui.theme_tokens import TOKENS


class ACFVerticalSoundingWidget(QWidget):
    """Real temperature/wind-speed vertical profile at a clicked map
    point - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._point: tuple[float, float] | None = None
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.text(
            0.5, 0.5, "Click a map to inspect a real column",
            transform=self.axis.transAxes, ha="center", va="center", color=TOKENS.text_muted, fontsize=8,
        )
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_title("VERTICAL COMPLEXITY SOUNDING", color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.canvas.draw_idle()

    def update_from_volume_and_point(
        self, volume: dict[str, Any], lat: float, lon: float, level_index: int | None = None
    ) -> None:
        """Real, immediate re-slice - no new solver run, matching this
        Workstation's own "compute once, re-slice per interaction"
        discipline (`vertical_profile_at_point()` is a real nearest-
        neighbour lookup into the already-computed volume)."""
        profile = vertical_profile_at_point(volume, lat, lon)
        self._point = (profile["lat"], profile["lon"])

        pressure = np.asarray(profile["pressure_profile_hpa"])
        temperature_c = np.asarray(profile["temperature_profile"]) - 273.15
        wind_speed = np.asarray(profile["wind_speed_profile"])

        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.plot(
            temperature_c, pressure, color=TOKENS.accent_primary, linewidth=1.6,
            marker="o", markersize=3, label="Temperature (°C)",
        )
        self.axis.set_xlabel("Temperature (°C)", color=TOKENS.accent_primary, fontsize=7)
        self.axis.set_ylabel("Pressure (hPa)", color=TOKENS.text_secondary, fontsize=7)
        self.axis.tick_params(axis="x", colors=TOKENS.accent_primary, labelsize=7)
        self.axis.tick_params(axis="y", colors=TOKENS.text_secondary, labelsize=7)

        wind_axis = self.axis.twiny()
        wind_axis.plot(
            wind_speed, pressure, color=TOKENS.warning, linewidth=1.2, linestyle="--",
            marker="o", markersize=3, label="Wind speed (m/s)",
        )
        wind_axis.set_xlabel("Wind speed (m/s)", color=TOKENS.warning, fontsize=7)
        wind_axis.tick_params(axis="x", colors=TOKENS.warning, labelsize=7)

        self.axis.invert_yaxis()  # surface at the bottom, meteorological convention
        if level_index is not None and 0 <= level_index < len(pressure):
            self.axis.axhline(float(pressure[level_index]), color=TOKENS.text_secondary, linewidth=0.8, linestyle=":")

        for spine in self.axis.spines.values():
            spine.set_color(TOKENS.border)
        for spine in wind_axis.spines.values():
            spine.set_color(TOKENS.border)
        self.axis.set_title(
            f"VERTICAL COMPLEXITY SOUNDING — {profile['lat']:.2f}°, {profile['lon']:.2f}°",
            color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left",
        )
        self.figure.subplots_adjust(left=0.2, right=0.95, top=0.8, bottom=0.16)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"has_point": self._point is not None, "point": self._point}
