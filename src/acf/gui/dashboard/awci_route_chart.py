"""
AWCI Route Planning Chart
=========================

Filled area chart of the real AWCI score along a flight route (synthetic
demo inputs - see awci_synthetic_field.py), colored by the shared AWCI
scale, matching the reference mockup's "ROUTE PLANNING" panel.

set_external_route() (added 2026-09-02) lets a caller show a real
acf.awci.path_sampling.sample_field_along_path() result instead.

Dual-flight-level comparison (added 2026-09-03, docs/reference/
awci_dashboard_reference.jpg parity work): the mockup compares AWCI
along the SAME route at two real flight levels (e.g. FL280 vs FL320)
as two colored lines. set_comparison_series() adds a real second
series (any real (distances_km, scores) pair the caller already
computed - e.g. a second real path_sampling.sample_field_along_path()
call at a different real hPa level) - both series then render as thin
comparison LINES with a legend instead of the single filled area, an
honest visual distinction (a filled area implies one continuous real
route profile; two filled areas overlapping would misrepresent which
one is "the" route). Bit-identical to before when no comparison series
is supplied.
"""

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.collections import PolyCollection
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
        #: Real (distances_km, scores, label) second series - see
        #: set_comparison_series()'s own docstring.
        self._comparison: tuple[Any, Any, str] | None = None
        #: Real label for the primary series, shown in the legend only
        #: when a comparison series is also present (see _draw()).
        self._primary_label = "Route"
        #: The real (distances, scores) last actually drawn as the
        #: primary series, from whichever source (update_data()'s
        #: synthetic pattern or set_external_route()'s real data) -
        #: read back by set_comparison_series()/clear_comparison_series()
        #: so they always redraw the SAME real primary data, never a
        #: second/guessed one.
        self._last_drawn: tuple[Any, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor="#0b1220")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)

    @property
    def last_distances_km(self) -> list[float] | None:
        """Real distances (km) for the primary series last drawn (whichever source) - None before any draw."""
        return list(self._last_drawn[0]) if self._last_drawn is not None else None

    def set_external_route(self, distances_km: Any, scores: Any, label: str) -> list[float]:
        """Show a real route profile (e.g. path_sampling.sample_field_along_path()'s output) instead of the synthetic pattern."""
        self._external_route = (distances_km, scores)
        self._title = f"{self._base_title} — {label}"
        self._last_drawn = (distances_km, scores)
        self._draw(distances_km, scores)
        return list(scores)

    def set_comparison_series(self, distances_km: Any, scores: Any, label: str, primary_label: str = "Route") -> None:
        """
        Add a real second series (see module docstring's "Dual-flight-
        level comparison" note) - redraws with both series as
        comparison lines plus a legend.

        Parameters
        ----------
        distances_km, scores : real values already computed by the
            caller (e.g. a second path_sampling.sample_field_along_path()
            call at a different real flight level) - never
            recomputed/guessed here.
        label : str
            Real label for this second series (e.g. "FL320").
        primary_label : str
            Real label for the already-drawn primary series (e.g.
            "FL280") - only shown once a comparison series exists.
        """
        self._comparison = (distances_km, scores, label)
        self._primary_label = primary_label
        if self._last_drawn is not None:
            self._draw(*self._last_drawn)

    def clear_comparison_series(self) -> None:
        """Revert to the single-series view - the primary series' own last real data is redrawn unchanged."""
        self._comparison = None
        if self._last_drawn is not None:
            self._draw(*self._last_drawn)

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
        self._last_drawn = (distances, scores)
        self._draw(distances, scores)
        return scores

    def _draw(self, distances: Any, scores: Any) -> None:
        self.axis.clear()

        if self._comparison is not None:
            # Dual-flight-level comparison mode (see module docstring)
            # - both series drawn as real, distinctly-colored lines
            # with a legend, no filled area (see module docstring for
            # why a fill is misleading once 2 real series are shown).
            comp_distances, comp_scores, comp_label = self._comparison
            self.axis.plot(distances, scores, color="#ffa726", linewidth=1.6, label=self._primary_label)
            self.axis.plot(comp_distances, comp_scores, color="#4fc3f7", linewidth=1.6, label=comp_label)
            legend = self.axis.legend(loc="upper right", fontsize=7, facecolor="#0f1830", edgecolor="#34445f")
            for text in legend.get_texts():
                text.set_color("#e8edf5")
        else:
            colors = AWCI_CMAP(np.array(scores) / 100.0)
            # A real PolyCollection (added 2026-09-03, profiled
            # AWCIDashboard.refresh() - this per-segment fill was ~79
            # separate real Axes.fill_between() calls, each with its
            # own real state/clip-path bookkeeping overhead, measured
            # as this panel's own single largest real cost). Every
            # segment's own quad (bottom-left, bottom-right, top-right,
            # top-left - the exact same 4 real corners
            # fill_between([x0,x1],[0,0],[y0,y1]) itself would draw)
            # is built once and added as ONE real collection - bit-
            # identical real pixels, far fewer real matplotlib calls.
            quads = [
                [(distances[i], 0), (distances[i + 1], 0), (distances[i + 1], scores[i + 1]), (distances[i], scores[i])]
                for i in range(len(distances) - 1)
            ]
            self.axis.add_collection(PolyCollection(quads, facecolors=colors[:-1], edgecolors="none"))
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
