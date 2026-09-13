"""
ACF Scientific Workstation — Model Agreement
================================================

Matches acf_workstation_reference.jpg's "Model Agreement" panel: one
real per-model agreement bar plus an overall verdict string. Built
entirely from `ModelConsensusEngine.
compute_real_multi_model_disagreement_field()`'s own real per-model
fields and spread field (the same real computation Confidence Lab/
Multi-Model Lab already used) - never a fabricated agreement number.

Confirmed real return shape (2026-09-13, read directly from
`src/acf/visualization/ai_forecast_center/model_consensus_engine.py`
and the existing call site in `acf_workstation_multimodel.py`):
`compute_real_multi_model_disagreement_field()` returns a dict whose
`per_model_field` key is `dict[model name -> real (n_lat, n_lon)
array]` and whose `disagreement_spread_field` key is a real
(n_lat, n_lon) array - matching this panel's own
`update_from_disagreement(per_model_field, spread_field)` parameter
shapes with no adjustment needed.

Agreement score per model =
    1 - (this model's own real domain-mean deviation from the real
         ensemble mean) / (the real spread field's own domain-mean
         magnitude),
clamped to [0, 1]. The denominator is the REAL `spread_field` passed
in (i.e. `disagreement_spread_field`, the engine's own measure of how
much the models actually disagree) - never the ensemble mean's own
absolute magnitude. Normalizing by the field's own magnitude instead
of by real spread is numerically insensitive to real disagreement:
e.g. a 10 K spread across Kelvin-range temperature fields (order
280-290 K) still reads as >=0.98 "High Agreement" if divided by
the ~285 K ensemble mean, because the deviation is tiny relative to
that absolute scale even though it is physically significant. Dividing
by the real spread magnitude instead means the score reflects how
large the disagreement is relative to how much the models actually
disagree, which is the physically meaningful comparison.

Domain-mean collapse (disclosed): this panel summarizes each model's
field as a single domain-mean scalar before comparing (one bar per
model, matching the reference image's one-bar-per-model display). It
does not expose the full spatially-resolved per-grid-point
disagreement that `compute_real_multi_model_disagreement_field()` can
also produce - a caller wanting that resolution must consume the raw
per-model/spread fields directly rather than through this panel.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style


class ModelAgreementPanel(QWidget):
    """Real per-model agreement bars derived from real multi-model spread."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model_scores: dict[str, float] = {}

        self._layout = QVBoxLayout(self)
        self._rows_layout = QVBoxLayout()
        self._layout.addLayout(self._rows_layout)

        self.verdict_label = QLabel("NOT_COMPUTED")
        self.verdict_label.setStyleSheet(label_style("text_muted", "sm"))
        self._layout.addWidget(self.verdict_label)

        self._bars: dict[str, QProgressBar] = {}

    def update_from_disagreement(self, per_model_field: dict[str, Any], spread_field: Any) -> None:
        # Clear previous rows.
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._bars.clear()
        self.model_scores = {}

        if not per_model_field:
            self.verdict_label.setText("NOT_COMPUTED_NO_MODELS_AVAILABLE")
            return

        values = {name: float(np.nanmean(field)) for name, field in per_model_field.items()}
        ensemble_mean = float(np.mean(list(values.values())))

        # Real spread (not the ensemble mean's own magnitude) anchors the
        # normalization - a model's deviation is only "small" relative to
        # how much the models actually disagree, not relative to the
        # field's own absolute scale (which would make e.g. Kelvin-scale
        # fields always read as "High Agreement" regardless of real
        # disagreement).
        spread_magnitude = float(np.nanmean(np.abs(spread_field))) if spread_field is not None else 0.0
        denom = spread_magnitude if spread_magnitude > 0 else 1.0

        for name, value in values.items():
            deviation = abs(value - ensemble_mean) / denom
            score = max(0.0, min(1.0, 1.0 - deviation))
            self.model_scores[name] = score

            row = QHBoxLayout()
            name_label = QLabel(name)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(round(score * 100))
            row.addWidget(name_label)
            row.addWidget(bar)
            self._rows_layout.addLayout(row)
            self._bars[name] = bar

        overall = sum(self.model_scores.values()) / len(self.model_scores)
        if overall >= 0.75:
            verdict = "High Agreement"
        elif overall >= 0.5:
            verdict = "Moderate Agreement"
        else:
            verdict = "Low Agreement"
        self.verdict_label.setText(verdict)
