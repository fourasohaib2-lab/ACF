"""
AWCI Vertical Cross-Section Panel
==================================

Filled contour of the real AWCICalculator score (synthetic demo inputs -
see awci_synthetic_field.py) along a flight path, altitude on the y-axis,
distance on the x-axis, with the flight track drawn over it - matching the
reference mockup's "VERTICAL CROSS-SECTION ALONG FLIGHT PATH" panel.

set_external_cross_section() (added 2026-09-02) lets a caller show a
real acf.awci.path_sampling.sample_volume_cross_section() result
instead - see that function's own docstring for what "real" means here
(native model levels, not standard pressure levels; path-averaged
local pressure per level).
"""

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP
from acf.gui.dashboard.awci_synthetic_field import cross_section_field

#: Rough US Standard Atmosphere pressure -> altitude (ft) conversion for the
#: y-axis, so the panel reads in feet like the reference (not hPa).
_HPA_TO_FT = [
    (1013, 0), (850, 4800), (700, 9900), (500, 18300),
    (400, 23600), (300, 30100), (250, 33900), (200, 38700), (150, 44600),
]


def _hpa_to_ft(hpa: float) -> float:
    """
    CORRECTED (found 2026-09-02 wiring real solver data into this
    panel): out-of-table pressures used to clamp to a single constant
    (_HPA_TO_FT[0][1] = 0 ft for anything above 1013 hPa,
    _HPA_TO_FT[-1][1] = 44600 ft for anything below 150 hPa) - fine for
    the synthetic demo pattern (always within the table's range), but
    CoupledEarthSolver's real state uses its own idealized pressure
    scale that can exceed 1013 hPa at the surface (see vertical_field.py
    - its own docstring documents this isn't literal sea-level
    pressure). Clamping silently collapsed 10 of a real 20-level
    profile's distinct levels onto the exact same y=0 ft in a real
    screenshot taken while verifying the cross-section wiring - a real,
    visually degenerate result, not the intended output. Now
    extrapolates linearly from the nearest boundary segment's slope
    instead, so out-of-range pressures still map to DISTINCT (if rough/
    approximate beyond the table's real US Standard Atmosphere data)
    altitudes rather than colliding.
    """
    for i in range(len(_HPA_TO_FT) - 1):
        p0, f0 = _HPA_TO_FT[i]
        p1, f1 = _HPA_TO_FT[i + 1]
        if p1 <= hpa <= p0:
            t = (p0 - hpa) / (p0 - p1)
            return f0 + t * (f1 - f0)

    if hpa > _HPA_TO_FT[0][0]:
        (p0, f0), (p1, f1) = _HPA_TO_FT[0], _HPA_TO_FT[1]
    else:
        (p0, f0), (p1, f1) = _HPA_TO_FT[-2], _HPA_TO_FT[-1]
    slope = (f1 - f0) / (p1 - p0)
    return f0 + slope * (hpa - p0)


class AWCICrossSection(QWidget):
    """Titled altitude-vs-distance AWCI heatmap along a great-circle-ish flight path."""

    def __init__(self, title: str = "VERTICAL CROSS-SECTION ALONG FLIGHT PATH", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_title = title
        self._title = title
        self._cruise_hpa = 300.0
        self._last_point_a: tuple[float, float] | None = None
        self._last_point_b: tuple[float, float] | None = None
        # (distances_km, levels_hpa, grid) from set_external_cross_section() -
        # see this module's docstring.
        self._external_cross_section: tuple[Any, Any, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0d1b2a")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)

    def set_external_cross_section(self, distances_km: Any, levels_hpa: Any, grid: Any, label: str) -> None:
        """Show a real cross-section (e.g. path_sampling.sample_volume_cross_section()'s output) instead of the synthetic pattern."""
        self._external_cross_section = (distances_km, levels_hpa, grid)
        self._title = f"{self._base_title} — {label}"
        self._draw(distances_km, levels_hpa, grid)

    def clear_external_cross_section(self) -> None:
        """Revert to the synthetic demo pattern for the last (point_a, point_b, cruise_hpa) passed to update_data()."""
        self._external_cross_section = None
        self._title = self._base_title
        if self._last_point_a is not None and self._last_point_b is not None:
            self.update_data(self._last_point_a, self._last_point_b, self._cruise_hpa)

    def update_data(self, point_a: tuple[float, float], point_b: tuple[float, float], cruise_hpa: float = 300.0) -> None:
        self._last_point_a = point_a
        self._last_point_b = point_b
        self._cruise_hpa = cruise_hpa
        if self._external_cross_section is not None:
            distances, levels_hpa, grid = self._external_cross_section
        else:
            distances, levels_hpa, grid = cross_section_field(point_a, point_b, n_along=60, n_levels=20)
        self._draw(distances, levels_hpa, grid)

    def _draw(self, distances: Any, levels_hpa: Any, grid: Any) -> None:
        self.axis.clear()
        levels_ft = [_hpa_to_ft(p) for p in levels_hpa]

        self.axis.contourf(distances, levels_ft, grid, levels=20, cmap=AWCI_CMAP, vmin=0, vmax=100)

        cruise_ft = _hpa_to_ft(self._cruise_hpa)
        self.axis.plot([distances[0], distances[-1]], [cruise_ft, cruise_ft], color="white", linewidth=1.5)
        mid_x = distances[len(distances) // 2]
        self.axis.plot(mid_x, cruise_ft, marker=">", color="white", markersize=10, markeredgecolor="black")

        self.axis.set_facecolor("#0a1929")
        self.axis.set_xlabel("Distance (km)", color="#b0b8c8", fontsize=8)
        self.axis.set_ylabel("Altitude (ft)", color="#b0b8c8", fontsize=8)
        self.axis.tick_params(colors="#b0b8c8", labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color("#3a4a6a")
        self.axis.set_title(self._title, color="#e0e0e0", fontsize=10, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.15)
        self.canvas.draw_idle()
