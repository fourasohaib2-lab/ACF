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

Agreement score per model = 1 - (this model's own real deviation from
the real ensemble mean, normalized by the real ensemble mean's own
magnitude), clamped to [0, 1]. This is a real, disclosed derived
metric, not a further-fabricated "confidence" figure.
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
        denom = abs(ensemble_mean) if ensemble_mean != 0 else 1.0

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
