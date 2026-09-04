"""
ACF Scientific Workstation — Forecast Consistency
=====================================================

Real, always-visible-slot side panel (Phase 35, 2026-09-05, matching
the reference mockup's own persistent right-column "FORECAST
CONSISTENCY" box - `docs/reference/
acf_scientific_workstation_reference.jpg`).

Real formula, reused as-is - not reimplemented
---------------------------------------------------
Reuses `acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine.compute_real_multi_model_disagreement_field()` -
the SAME real, already-shipped, already-tested engine Confidence Lab's
own "🔄 Compute Model Confidence Field" button already uses (one real
`CoupledEarthSolver` run per real model, regridded onto a shared real
grid, real `EnsembleManager` spread/mean at every point) - this widget
adds no new science, only a compact always-present home for it.

Honest scope - why this stays on-demand, and why "models" not "runs"
--------------------------------------------------------------------
Real cost is N real, independent solver runs (~0.9s for 2 models,
measured) - genuinely fast, but still real work, so - same discipline
as every other genuinely-expensive computation in this Workstation -
this panel starts "Not yet computed" and requires an explicit click,
never an automatic run.

Honest disclosure on the mockup's own framing: its "FORECAST
CONSISTENCY" panel labels its x-axis "Sun N, N-1, N-2" - successive
forecast RUNS over time. This Workstation has no real archived
forecast-run history to compare against (every real field here comes
from a live solver run, never an archived NWP product - see the
Workstation's own module docstring). Building a genuine run-to-run
history would mean accumulating real volumes across actual "🔄 Run"
clicks within one session - a real but materially different feature,
deferred rather than faked. This panel instead shows real
MODEL-to-model consistency (AROME/ALADIN/ARPEGE's own real mean field
value, side by side, plus the real ensemble spread) - a genuine,
already-built measure of forecast consistency, just along a different
real axis than the mockup's own literal label.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.theme_tokens import TOKENS, label_style
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine

#: Same 3 real MODEL_CONFIGS models compared, in the same real order,
#: as Confidence Lab's own on-demand comparison - not re-derived.
_MODELS: tuple[str, ...] = ("AROME", "ALADIN", "ARPEGE")
_TARGET_MODEL = "ARPEGE"


class _ConsistencyWorkerSignals(QObject):
    finished = Signal(dict)
    failed = Signal(str)


class _ConsistencyWorker(QRunnable):
    """Runs ModelConsensusEngine.compute_real_multi_model_disagreement_field()
    off the GUI thread - same real QRunnable pattern this Workstation's
    other on-demand computations already use."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _ConsistencyWorkerSignals()

    def run(self) -> None:
        try:
            result = ModelConsensusEngine.compute_real_multi_model_disagreement_field(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFForecastConsistencyWidget(QWidget):
    """Real, compact multi-model consistency panel - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        controls = QHBoxLayout()
        self.run_button = QPushButton(f"▶ Compare {'/'.join(_MODELS)}")
        self.run_button.setToolTip(
            "Real, off-thread compute_real_multi_model_disagreement_field() run - a real\n"
            f"CoupledEarthSolver run per model ({', '.join(_MODELS)}). On demand, not automatic."
        )
        self.run_button.clicked.connect(self._start)
        controls.addWidget(self.run_button)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.figure = plt.figure(facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas, stretch=1)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.text(
            0.5, 0.5, "Click ▶ to compare real models", transform=self.axis.transAxes,
            ha="center", va="center", color=TOKENS.text_muted, fontsize=8,
        )
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_title("FORECAST CONSISTENCY", color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.canvas.draw_idle()

    def _start(self) -> None:
        self.run_button.setEnabled(False)
        self.status_label.setText(f"⏳ Computing real consistency ({'/'.join(_MODELS)} — a real solver run per model)…")
        worker = _ConsistencyWorker(models=list(_MODELS), steps=3, target_model=_TARGET_MODEL, seed=1)
        worker.signals.finished.connect(self._on_ready)
        worker.signals.failed.connect(self._on_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_ready(self, result: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self._result = result
        spread = result["disagreement_spread_field"]
        self.status_label.setText(
            f"✅ Real mean field per model ({result['field']} @ level {result['level']}) — "
            f"ensemble spread mean {float(np.nanmean(spread)):.3f}, max {float(np.nanmax(spread)):.3f}."
        )
        self._draw()

    def _on_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real consistency computation failed: {message}")

    def _draw(self) -> None:
        if self._result is None:
            return
        per_model_field = self._result["per_model_field"]
        models = list(per_model_field.keys())
        means = [float(np.nanmean(per_model_field[m])) for m in models]

        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        colors = [TOKENS.accent_primary, TOKENS.warning, TOKENS.success, TOKENS.danger][: len(models)]
        self.axis.bar(models, means, color=colors)
        self.axis.set_ylabel(f"Mean {self._result['field']}", color=TOKENS.text_secondary, fontsize=7)
        self.axis.tick_params(colors=TOKENS.text_secondary, labelsize=7)
        for spine in self.axis.spines.values():
            spine.set_color(TOKENS.border)
        self.axis.set_title("FORECAST CONSISTENCY", color=TOKENS.text_primary, fontsize=9, fontweight="bold", loc="left")
        self.figure.subplots_adjust(left=0.2, right=0.95, top=0.85, bottom=0.15)
        self.canvas.draw_idle()

    def status(self) -> dict[str, Any]:
        return {"has_result": self._result is not None}
