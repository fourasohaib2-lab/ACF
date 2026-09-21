"""
AWCI Model Spread Chart
=========================

Real multi-model consensus/spread bar chart - explicit user request
"vasy respecte le prompt" (docs/ACF_MASTER_PROMPT.md sections 18-19,
27-29), matching the general ACF dashboard reference mockup's
"MULTI-MODEL CONSENSUS SPREAD" panel.

Fed from acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine.compute_real_multi_model_disagreement() - real
per-model values from ACF's own solver run once per real model grid
configuration (that function's own honest_limitation: standing in for
real archived NWP output, not a fabricated placeholder - see its own
docstring for the full disclosure).
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.gui.theme_tokens import TOKENS


class AWCIModelSpreadChart(QWidget):
    """Titled real per-model bar chart with the real mean/spread annotated."""

    def __init__(self, title: str = "MULTI-MODEL CONSENSUS SPREAD", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.text(0.5, 0.5, "Not yet computed\n(click 🔄 Compute Consensus)", transform=self.axis.transAxes, ha="center", va="center", color=TOKENS.text_muted, fontsize=9)
        self.axis.set_title(self._title, color=TOKENS.text_primary, fontsize=10, fontweight="bold", loc="left")
        self.canvas.draw_idle()

    def set_data(self, per_model_value: dict[str, float], disagreement_mean: float, disagreement_spread: float, variable_label: str) -> None:
        """Real per-model values, e.g. ModelConsensusEngine.compute_real_multi_model_disagreement()'s own `per_model_value`/`disagreement_mean`/`disagreement_spread`."""
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)

        models = list(per_model_value.keys())
        values = list(per_model_value.values())
        colors = [TOKENS.accent_primary if abs(v - disagreement_mean) <= disagreement_spread else TOKENS.warning for v in values]
        self.axis.bar(models, values, color=colors, edgecolor=TOKENS.border)
        self.axis.axhline(disagreement_mean, color=TOKENS.text_secondary, linewidth=1.0, linestyle="--", label=f"Mean = {disagreement_mean:.2f}")

        self.axis.set_ylabel(variable_label, color=TOKENS.text_secondary, fontsize=8)
        self.axis.tick_params(colors=TOKENS.text_secondary, labelsize=8)
        for spine in self.axis.spines.values():
            spine.set_color(TOKENS.border)
        self.axis.legend(fontsize=7, facecolor=TOKENS.bg_card, edgecolor=TOKENS.border, labelcolor=TOKENS.text_primary)
        self.axis.set_title(f"{self._title} — spread={disagreement_spread:.2f}", color=TOKENS.text_primary, fontsize=10, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.15, right=0.97, top=0.85, bottom=0.15)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"figure": self.figure is not None, "axis": self.axis is not None}
