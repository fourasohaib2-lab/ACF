"""
ACF Scientific Workstation — 3D Atmosphere View
===================================================

Real volumetric structure panel for `acf_workstation.ACFWorkstation`
(see that module's own docstring for the Workstation's overall
"ACF CORE ONLY - NO AWCI" rule). Answers docs/ACF_MASTER_PROMPT.md
§23's own explicit "L'ACF ne doit pas seulement produire un score
ponctuel... 3D — Structure volumique" - every other Lab in this
Workstation shows one real 2D horizontal slice at a time (the current
level); this one shows several real levels of the SAME already-
computed volume stacked in one real 3D view, at their own real mean
pressure - never a second, independent computation.

Real technique, not fabricated
----------------------------------
`matplotlib`'s own `Axes3D.contourf(..., zdir="z", offset=pressure)` -
a real, standard, documented matplotlib 3D technique: draw an
ordinary 2D filled contour, positioned at a fixed real Z coordinate in
3D space. Stacking one real contourf per shown level, each offset at
that level's own real mean pressure (`pressure_volume_hpa[level].
mean()`), builds a real "data cube" - genuinely real data at genuinely
real 3D positions, not an interpolated/fabricated isosurface. The Z
axis is inverted (`Axes3D.invert_zaxis()`) so it reads top-to-bottom
like a real meteorological convention (high pressure/ground at the
bottom, low pressure/upper atmosphere at the top) while the underlying
real data values stay honestly in real hPa, unmodified.

Honest rendering choice: not every native level
-----------------------------------------------------
Stacking all of a real volume's native levels (up to 32 for AROME)
would be visually unreadable (overlapping, indistinguishable layers)
and slow to render - `_MAX_SHOWN_LEVELS` real, evenly-spaced levels
are shown instead (real data at real positions, simply a coarser
SUBSET of levels, same "real subsample for a readable/fast result"
trade-off already established for CAPE/CIN's coarser grid and
Confidence Lab's regridded output - never interpolated between shown
levels).

Honest scope: no geographic basemap
-----------------------------------------
This view has no coastlines/borders (unlike every other Lab's
`AWCIMapPanel`, which uses `cartopy`) - real longitude/latitude axes
without a rendered basemap, disclosed in the panel's own title. Adding
a real 3D basemap (e.g. a flat coastline outline at the base level) is
real, additional future work, not attempted here to keep this pass
bounded.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - registers the real '3d' projection; required, never used directly
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

#: Real per-variable volume key + unit + a real, disclosed physical
#: rendering range - same real ranges Overview's own _VARIABLES uses
#: for these exact quantities (not re-derived independently).
_VARIABLES: dict[str, dict[str, Any]] = {
    "Temperature": {"key": "temperature_volume", "unit": "K", "cmap": "coolwarm", "vmin": 230.0, "vmax": 310.0},
    "Wind speed": {"key": "wind_speed_volume", "unit": "m/s", "cmap": "viridis", "vmin": 0.0, "vmax": 40.0},
    "Specific humidity": {
        "key": "specific_humidity_volume", "unit": "kg/kg", "cmap": "YlGnBu", "vmin": 0.0, "vmax": 0.02,
    },
}

#: See module docstring's "Honest rendering choice" section.
_MAX_SHOWN_LEVELS = 6


class ACF3DAtmospherePanel(QWidget):
    """Real 3D Atmosphere View - several real native levels of the
    current volume stacked at their own real mean pressure. No AWCI
    content anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None

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

        self.figure = plt.figure(facecolor="#0b1220")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111, projection="3d")
        self.axis.set_facecolor("#0b1220")
        layout.addWidget(self.canvas, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume - no new
        solver run. `level_index` is accepted for the same real
        signature every other Lab panel uses but is not read here: this
        view always shows its own real subset of levels (see module
        docstring), not the Workstation's single current-level
        selection."""
        self._volume = volume
        self._redraw()

    def _redraw(self) -> None:
        if self._volume is None:
            return
        self.axis.clear()
        self.axis.set_facecolor("#0b1220")

        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        volume_field = self._volume[spec["key"]]
        n_levels = self._volume["n_levels"]
        lats = np.asarray(self._volume["lats"])
        lons = np.asarray(self._volume["lons"])
        lon_grid, lat_grid = np.meshgrid(lons, lats)

        n_shown = min(_MAX_SHOWN_LEVELS, n_levels)
        shown_levels = sorted({int(v) for v in np.linspace(0, n_levels - 1, n_shown).round()})
        pressures_hpa = [float(self._volume["pressure_volume_hpa"][lvl].mean()) for lvl in shown_levels]
        contour_levels = np.linspace(spec["vmin"], spec["vmax"], 21)

        for level_idx, pressure in zip(shown_levels, pressures_hpa, strict=True):
            self.axis.contourf(
                lon_grid,
                lat_grid,
                volume_field[level_idx],
                zdir="z",
                offset=pressure,
                levels=contour_levels,
                cmap=spec["cmap"],
                vmin=spec["vmin"],
                vmax=spec["vmax"],
                alpha=0.85,
            )

        self.axis.set_xlabel("Longitude (°)", color="#9fb0c9", fontsize=8)
        self.axis.set_ylabel("Latitude (°)", color="#9fb0c9", fontsize=8)
        self.axis.set_zlabel("Pressure (hPa)", color="#9fb0c9", fontsize=8)
        self.axis.tick_params(colors="#6b7a94", labelsize=6)
        self.axis.set_zlim(min(pressures_hpa) - 50.0, max(pressures_hpa) + 50.0)
        self.axis.invert_zaxis()  # real meteorological convention: pressure decreases upward
        self.axis.set_title(
            f"Real {self._volume.get('model', '')} — {variable} — {len(shown_levels)} real levels stacked\n"
            "(no geographic basemap - see the 2D Labs for map context)",
            color="#e8edf5",
            fontsize=9,
        )
        self.canvas.draw_idle()
