"""
AWCI Vertical Cross-Section Panel
==================================

Filled contour of the real AWCICalculator score (synthetic demo inputs -
see awci_synthetic_field.py) along a flight path, altitude on the y-axis,
distance on the x-axis, with the flight track drawn over it - matching the
reference mockup's "VERTICAL CROSS-SECTION ALONG FLIGHT PATH" panel.
"""

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
    for i in range(len(_HPA_TO_FT) - 1):
        p0, f0 = _HPA_TO_FT[i]
        p1, f1 = _HPA_TO_FT[i + 1]
        if p1 <= hpa <= p0:
            t = (p0 - hpa) / (p0 - p1)
            return f0 + t * (f1 - f0)
    return _HPA_TO_FT[-1][1] if hpa < _HPA_TO_FT[-1][0] else _HPA_TO_FT[0][1]


class AWCICrossSection(QWidget):
    """Titled altitude-vs-distance AWCI heatmap along a great-circle-ish flight path."""

    def __init__(self, title: str = "VERTICAL CROSS-SECTION ALONG FLIGHT PATH", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0d1b2a")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)

    def update_data(self, point_a: tuple[float, float], point_b: tuple[float, float], cruise_hpa: float = 300.0) -> None:
        self.axis.clear()
        distances, levels_hpa, grid = cross_section_field(point_a, point_b, n_along=60, n_levels=20)
        levels_ft = [_hpa_to_ft(p) for p in levels_hpa]

        self.axis.contourf(distances, levels_ft, grid, levels=20, cmap=AWCI_CMAP, vmin=0, vmax=100)

        cruise_ft = _hpa_to_ft(cruise_hpa)
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
