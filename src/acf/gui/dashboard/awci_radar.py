"""
AWCI Radar (Spider) Chart
=========================

Polar radar chart of the AWCI module decomposition, matching the reference
mockup's "AWCI COMPONENTS" hexagonal radar - built with matplotlib's polar
projection rather than the horizontal-bar AWCIDecomposition widget, for a
closer visual match to that reference.
"""

import math

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

_AXES = [
    ("dynamic", "Dynamic\nComplexity"),
    ("thermodynamic", "Thermodynamic\nComplexity"),
    ("convective", "Convective\nComplexity"),
    ("microphysical", "Microphysical\nComplexity"),
    ("topographic", "Topographic\nComplexity"),
    ("temporal", "Temporal\nComplexity"),
]


class AWCIRadar(QWidget):
    """Titled radar chart of the 6 AWCI module scores (0-100 each)."""

    def __init__(self, title: str = "AWCI COMPONENTS", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0d1b2a")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1, projection="polar")

        self.update_data({})

    def update_data(self, module_scores: dict[str, float]) -> None:
        """module_scores: AWCICalculator.calculate()['module_scores'] (0-100 each, [0,1] internally)."""
        self.axis.clear()

        n = len(_AXES)
        angles = [i / n * 2 * math.pi for i in range(n)]
        values = [module_scores.get(key, 0.0) for key, _ in _AXES]
        angles_closed = angles + angles[:1]
        values_closed = values + values[:1]

        self.axis.set_facecolor("#0d1b2a")
        self.axis.plot(angles_closed, values_closed, color="#ff8c00", linewidth=2)
        self.axis.fill(angles_closed, values_closed, color="#ff8c00", alpha=0.35)

        self.axis.set_xticks(angles)
        self.axis.set_xticklabels([label for _, label in _AXES], color="#c0c8d8", fontsize=7)
        self.axis.set_ylim(0, 100)
        self.axis.set_yticks([25, 50, 75, 100])
        self.axis.set_yticklabels(["25", "50", "75", "100"], color="#8090a8", fontsize=6)
        self.axis.spines["polar"].set_color("#3a4a6a")
        self.axis.grid(color="#2a3a5a", linewidth=0.6)
        self.axis.set_title(self._title, color="#e0e0e0", fontsize=10, fontweight="bold", pad=14)
        self.figure.subplots_adjust(left=0.12, right=0.88, top=0.85, bottom=0.08)
        self.canvas.draw_idle()
