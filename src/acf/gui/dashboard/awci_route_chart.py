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
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import AWCI_CMAP, level_for, risk_qcolor
from acf.gui.dashboard.awci_synthetic_field import route_profile
from acf.gui.theme_tokens import TOKENS


class AWCIRouteChart(QWidget):
    """Titled AWCI-vs-distance filled chart along a route."""

    def __init__(
        self,
        title: str = "ROUTE PLANNING — AWCI along route",
        parent: QWidget | None = None,
        figsize_scale: float = 1.0,
    ) -> None:
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

        # figsize width trimmed 6.0->5.4in (2026-09-07, real bug found by
        # rendering the dashboard at a real 1920x1080 size and looking at
        # the screenshot, not just checking scrollbar metrics): the
        # ~60px this frees lets AWCIRiskSummary's badge column (op_row,
        # right next to this canvas) keep its real minimumWidth instead
        # of being squeezed by the layout engine down to partially-
        # clipped text ("Extreme" rendering as "Extrem") - see
        # _RiskRow's own badge label for the matching minimumWidth fix.
        # figsize_scale (added same day, "assure toi que la resolution
        # est adaptable selon le type d'ecran") - see
        # AWCICrossSection's own matching comment.
        scale = max(0.6, figsize_scale)
        self.figure = plt.figure(figsize=(5.4 * scale, 1.6 * scale), facecolor="#0b1220")
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


class AWCIRouteSegmentTable(QFrame):
    """Real "Route Segments" breakdown (added 2026-09-13, closing
    Master Prompt V3 §20's "for each segment calculate/display AWCI,
    dominant risk class; highlight critical segments" - the reference
    photo's own per-leg segment list, e.g. "ALG -> TUN" / "TUN -> FCO").

    Honest scope: this dashboard's own route is a single real 2-point
    great-circle path (departure/arrival - see AWCIDashboard's own
    route selector), not yet a multi-waypoint itinerary with named
    intermediate airports - showing fabricated intermediate airport
    names would misrepresent that. Segments are instead real, honest
    equal-distance buckets of the SAME real per-point samples
    AWCIRouteChart already plots (never a second/independent
    computation) - each row's AWCI is the real mean of every real
    sampled point whose real distance falls in that bucket, and its
    risk level reuses the exact same shared AWCI scale
    (acf.gui.dashboard.awci_colors.level_for()) every other panel on
    this dashboard already uses. The single worst segment is flagged
    "Critical Zone" using the exact same real >= 60 threshold
    AWCIRouteChart's own "High complexity area" chart annotation
    already uses (see this module's own _draw()) - never a second,
    independently-chosen threshold.
    """

    #: Same real threshold as this module's own _draw() "High
    #: complexity area" chart annotation - one real, shared definition
    #: of "critical" for this route, never two independently-chosen
    #: thresholds that could silently disagree.
    CRITICAL_AWCI_THRESHOLD = 60.0

    def __init__(self, n_segments: int = 4, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._n_segments = max(1, n_segments)
        self.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_sm}px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        title = QLabel("Route Segments")
        title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 9px; font-weight: bold; border: none;")
        layout.addWidget(title)

        header_row = QHBoxLayout()
        for text, stretch in (("Segment", 3), ("AWCI", 1), ("Risk", 2)):
            header_label = QLabel(text)
            header_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 8px; border: none;")
            header_row.addWidget(header_label, stretch=stretch)
        layout.addLayout(header_row)

        self._rows_layout = QVBoxLayout()
        self._rows_layout.setSpacing(1)
        layout.addLayout(self._rows_layout)

        self.critical_label = QLabel("")
        self.critical_label.setWordWrap(True)
        self.critical_label.setStyleSheet(f"color: {TOKENS.warning}; font-size: 8px; font-weight: bold; border: none; margin-top: 2px;")
        self.critical_label.setVisible(False)
        layout.addWidget(self.critical_label)

    def update_data(self, distances_km: Any, scores: Any) -> None:
        """`distances_km`/`scores` are the SAME real arrays
        AWCIRouteChart._draw() itself just plotted (e.g. from
        AWCIRouteChart.last_distances_km + the caller's own already-
        computed real scores) - never resampled/recomputed here."""
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.critical_label.setVisible(False)

        distances = list(distances_km) if distances_km is not None else []
        values = list(scores) if scores is not None else []
        if len(distances) < 2 or len(values) < 2 or len(distances) != len(values):
            empty = QLabel("No real route sampled yet.")
            empty.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 8px; border: none;")
            self._rows_layout.addWidget(empty)
            return

        span_start, span_end = distances[0], distances[-1]
        span = span_end - span_start
        n_segments = self._n_segments
        worst_mean = -1.0
        worst_label = ""
        for seg_idx in range(n_segments):
            seg_start = span_start + span * seg_idx / n_segments
            seg_end = span_start + span * (seg_idx + 1) / n_segments
            # Real, inclusive-both-ends bucketing at the boundaries so
            # the first/last real sampled point are never silently
            # dropped from every segment's own real mean.
            bucket = [
                value for distance, value in zip(distances, values)
                if (seg_start <= distance <= seg_end) or (seg_idx == n_segments - 1 and distance == span_end)
            ]
            if not bucket:
                continue
            mean_awci = float(np.mean(bucket))
            level = level_for(mean_awci)
            seg_label = f"{seg_start:.0f}–{seg_end:.0f} km"
            if mean_awci > worst_mean:
                worst_mean = mean_awci
                worst_label = seg_label

            row = QHBoxLayout()
            name_label = QLabel(seg_label)
            name_label.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 8px; border: none;")
            awci_label = QLabel(f"{mean_awci:.0f}")
            awci_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 8px; border: none;")
            color = risk_qcolor(level)
            risk_label = QLabel(level)
            risk_label.setStyleSheet(
                f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 8px; font-weight: bold; border: none;"
            )
            row.addWidget(name_label, stretch=3)
            row.addWidget(awci_label, stretch=1)
            row.addWidget(risk_label, stretch=2)
            self._rows_layout.addLayout(row)

        if worst_mean >= self.CRITICAL_AWCI_THRESHOLD:
            self.critical_label.setText(f"⚠ Critical Zone: {worst_label} (AWCI {worst_mean:.0f})")
            self.critical_label.setVisible(True)
