"""
AWCI Route Planning Chart
=========================

Filled area chart of the real AWCI score along a flight route (synthetic
demo inputs - see awci_synthetic_field.py), colored by the shared AWCI
scale, matching the reference mockup's "ROUTE PLANNING" panel.

set_external_route() (added 2026-09-02) lets a caller show a real
acf.awci.path_sampling.sample_field_along_path() result instead.
"""

from typing import Any

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
        self._base_title = title
        self._title = title
        self._last_point_a: tuple[float, float] | None = None
        self._last_point_b: tuple[float, float] | None = None
        self._last_cruise_hpa = 300.0
        # (distances_km, scores) from set_external_route() - see module docstring.
        self._external_route: tuple[Any, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0b1220")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)

    def set_external_route(self, distances_km: Any, scores: Any, label: str) -> list[float]:
        """Show a real route profile (e.g. path_sampling.sample_field_along_path()'s output) instead of the synthetic pattern."""
        self._external_route = (distances_km, scores)
        self._title = f"{self._base_title} — {label}"
        self._draw(distances_km, scores)
        return list(scores)

    def clear_external_route(self) -> list[float] | None:
        """Revert to the synthetic demo pattern for the last (point_a, point_b, cruise_hpa) passed to update_data()."""
        self._external_route = None
        self._title = self._base_title
        if self._last_point_a is not None and self._last_point_b is not None:
            return self.update_data(self._last_point_a, self._last_point_b, self._last_cruise_hpa)
        return None

    def update_data(
        self, point_a: tuple[float, float], point_b: tuple[float, float], cruise_hpa: float = 300.0
    ) -> list[float]:
        self._last_point_a = point_a
        self._last_point_b = point_b
        self._last_cruise_hpa = cruise_hpa
        if self._external_route is not None:
            distances, scores = self._external_route
        else:
            distances, scores = route_profile(point_a, point_b, n_points=80, flight_level_hpa=cruise_hpa)
        self._draw(distances, scores)
        return scores

    def _draw(self, distances: Any, scores: Any) -> None:
        self.axis.clear()
        colors = AWCI_CMAP(np.array(scores) / 100.0)
        for i in range(len(distances) - 1):
            self.axis.fill_between(distances[i : i + 2], [0, 0], scores[i : i + 2], color=colors[i], linewidth=0)
        self.axis.plot(distances, scores, color="#e8edf5", linewidth=1.0)

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

        self.axis.set_facecolor("#0f1830")
        self.axis.set_ylim(0, 100)
        self.axis.set_xlabel("Distance (km)", color="#9fb0c9", fontsize=8)
        self.axis.set_ylabel("AWCI", color="#9fb0c9", fontsize=8)
        self.axis.tick_params(colors="#9fb0c9", labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color("#34445f")
        self.axis.set_title(self._title, color="#e8edf5", fontsize=10, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.18)
        self.canvas.draw_idle()
