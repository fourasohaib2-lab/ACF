"""
AWCI Route Planning Chart
=========================

Filled area chart of the real AWCI score along a flight route (synthetic
demo inputs - see awci_synthetic_field.py), colored by the shared AWCI
scale, matching the reference mockup's "ROUTE PLANNING" panel.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP
from acf.gui.dashboard.awci_synthetic_field import route_profile


class AWCIRouteChart(QWidget):
    """Titled AWCI-vs-distance filled chart along a route."""

    def __init__(self, title: str = "ROUTE PLANNING — AWCI along route", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0d1b2a")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)

    def update_data(
        self, point_a: tuple[float, float], point_b: tuple[float, float], cruise_hpa: float = 300.0
    ) -> list[float]:
        self.axis.clear()
        distances, scores = route_profile(point_a, point_b, n_points=80, flight_level_hpa=cruise_hpa)

        colors = AWCI_CMAP(np.array(scores) / 100.0)
        for i in range(len(distances) - 1):
            self.axis.fill_between(distances[i : i + 2], [0, 0], scores[i : i + 2], color=colors[i], linewidth=0)
        self.axis.plot(distances, scores, color="#e0e0e0", linewidth=1.0)

        max_i = int(np.argmax(scores))
        if scores[max_i] >= 60:
            self.axis.annotate(
                "High complexity area",
                xy=(distances[max_i], scores[max_i]),
                xytext=(distances[max_i], min(98, scores[max_i] + 12)),
                color="#ffb74d",
                fontsize=7,
                ha="center",
                arrowprops={"arrowstyle": "->", "color": "#ffb74d"},
            )

        self.axis.set_facecolor("#0a1929")
        self.axis.set_ylim(0, 100)
        self.axis.set_xlabel("Distance (km)", color="#b0b8c8", fontsize=8)
        self.axis.set_ylabel("AWCI", color="#b0b8c8", fontsize=8)
        self.axis.tick_params(colors="#b0b8c8", labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color("#3a4a6a")
        self.axis.set_title(self._title, color="#e0e0e0", fontsize=10, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.18)
        self.canvas.draw_idle()

        return scores
