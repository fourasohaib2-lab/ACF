"""
AWCI Evolution Chart
======================

Real AWCI(t) time series - explicit user request "vasy respecte le
prompt" (docs/ACF_MASTER_PROMPT.md sections 27-29), matching the
general ACF dashboard reference mockup's "AWCI EVOLUTION (24h)" panel
(docs/reference/acf_dashboard_reference.jpg).

Fed from the SAME real awci.complexity.temporal_field.
compute_real_complexity_evolution() trajectory that already drives the
AWCI dashboard's "▶ Play Evolution (4D)" animation - one real
continuous CoupledEarthSolver run, not a second computation and not a
fabricated smooth curve.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.gui.theme_tokens import TOKENS


class AWCIEvolutionChart(QWidget):
    """Titled real AWCI(t) line chart, one real value per real frame."""

    def __init__(self, title: str = "AWCI EVOLUTION", parent: QWidget | None = None, figsize_scale: float = 1.0) -> None:
        super().__init__(parent)
        self._title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Real bug found 2026-09-20 ("un seul écran sans scroller"
        # layout audit): unlike every sibling chart in this analysis
        # row (AWCICrossSection/AWCIRouteChart), this one never took a
        # figsize/figsize_scale - matplotlib's own default figsize
        # (6.4x4.8in) meant this single panel alone demanded ~480px of
        # real height, far more than its 4 siblings, forcing the whole
        # analysis row (a QHBoxLayout, one shared row height) to grow
        # to match it - confirmed the single largest contributor to
        # this dashboard's real vertical overflow past 1080px. Same
        # real screen_scale-driven sizing as its siblings now, same
        # honest data underneath (nothing about the real series drawn
        # changes, only the figure's own physical size).
        scale = max(0.6, figsize_scale)
        self.figure = plt.figure(figsize=(5.4 * scale, 1.3 * scale), facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._current_frame_marker = None
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.text(0.5, 0.5, "No real evolution yet", transform=self.axis.transAxes, ha="center", va="center", color=TOKENS.text_muted, fontsize=9)
        self.axis.set_title(self._title, color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.canvas.draw_idle()

    def set_series(self, valid_time_hours: list[float], awci_mean_per_frame: list[float], awci_max_per_frame: list[float], current_frame_index: int | None = None) -> None:
        """
        Real per-frame series - `awci_mean_per_frame`/`awci_max_per_frame`
        are the real mean/max of one real
        compute_real_complexity_evolution() frame's `awci_evolution`
        surface-level slice (computed by the caller, not here - this
        widget only ever draws real numbers it is handed).
        """
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)

        self.axis.plot(valid_time_hours, awci_mean_per_frame, color=TOKENS.accent_primary, linewidth=1.6, marker="o", markersize=3, label="Mean AWCI")
        self.axis.plot(valid_time_hours, awci_max_per_frame, color=TOKENS.warning, linewidth=1.2, linestyle="--", marker="o", markersize=3, label="Max AWCI")

        if current_frame_index is not None and 0 <= current_frame_index < len(valid_time_hours):
            self.axis.axvline(valid_time_hours[current_frame_index], color=TOKENS.text_secondary, linewidth=0.8, linestyle=":")

        self.axis.set_xlabel("Valid time (h)", color=TOKENS.text_secondary, fontsize=8)
        self.axis.set_ylabel("AWCI", color=TOKENS.text_secondary, fontsize=8)
        self.axis.set_ylim(0, 100)
        self.axis.tick_params(colors=TOKENS.text_secondary, labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color(TOKENS.border)
        self.axis.legend(fontsize=7, facecolor=TOKENS.bg_card, edgecolor=TOKENS.border, labelcolor=TOKENS.text_primary)
        self.axis.set_title(self._title, color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.12, right=0.97, top=0.85, bottom=0.2)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"figure": self.figure is not None, "axis": self.axis is not None}
