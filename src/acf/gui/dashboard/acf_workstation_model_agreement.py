"""
ACF Scientific Workstation — Model Agreement
================================================

Matches acf_workstation_reference.jpg's "Model Agreement" panel: one
real per-model agreement bar (model name left, colored bar, real score
right) plus an overall verdict string shown in the card's own title row
(the composer places `verdict_label` there via `_section_box`'s
`corner_widget`, matching the reference image's "Model Agreement ...
Low Agreement" single header line). Built entirely from
`ModelConsensusEngine.compute_real_multi_model_disagreement_field()`'s
own real per-model fields and spread field (the same real computation
Confidence Lab/Multi-Model Lab already used) - never a fabricated
agreement number.

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
absolute magnitude (numerically insensitive to real disagreement - see
git history for the measured example this was fixed against).

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
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from acf.gui.dashboard.acf_workstation_gauges import HorizontalBarGauge
from acf.gui.theme_tokens import label_style

#: Real, stable per-model bar colors - visually matches
#: acf_workstation_reference.jpg's own AROME/ALADIN/ARPEGE/WRF row
#: colors. A model name outside this table (this Workstation runs
#: real solvers under these 4 real named configurations - see
#: acf.awci.model_configs.MODEL_CONFIGS - but a future 5th model would
#: still need a bar) cycles through the same palette rather than
#: crashing.
_MODEL_COLORS: dict[str, str] = {
    "AROME": "#3b82f6",
    "ALADIN": "#22c55e",
    "ARPEGE": "#f97316",
    "WRF": "#a855f7",
}
_FALLBACK_PALETTE = ["#3b82f6", "#22c55e", "#f97316", "#a855f7", "#0ea5e9", "#ec4899"]


class ModelAgreementPanel(QWidget):
    """Real per-model agreement bars derived from real multi-model spread."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model_scores: dict[str, float] = {}

        self._rows_layout = QVBoxLayout(self)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(10)

        # Not added to this panel's own layout - the composer places it
        # in the card's title row (`_wrap_in_box(..., corner_widget=...)`),
        # matching the reference image's single "Model Agreement ... Low
        # Agreement" header line. Still a real, live-updated label.
        self.verdict_label = QLabel("NOT_COMPUTED")
        self.verdict_label.setStyleSheet(label_style("warning", "xs", "bold"))

        self._bars: dict[str, HorizontalBarGauge] = {}
        self._value_labels: dict[str, QLabel] = {}

    def update_from_disagreement(self, per_model_field: dict[str, Any], spread_field: Any) -> None:
        # Clear previous rows.
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            inner_layout = item.layout()
            if inner_layout is not None:
                while inner_layout.count():
                    inner_item = inner_layout.takeAt(0)
                    if inner_item.widget():
                        inner_item.widget().deleteLater()
        self._bars.clear()
        self._value_labels.clear()
        self.model_scores = {}

        if not per_model_field:
            self.verdict_label.setText("NOT_COMPUTED_NO_MODELS_AVAILABLE")
            return

        values = {name: float(np.nanmean(field)) for name, field in per_model_field.items()}
        ensemble_mean = float(np.mean(list(values.values())))

        spread_magnitude = float(np.nanmean(np.abs(spread_field))) if spread_field is not None else 0.0
        denom = spread_magnitude if spread_magnitude > 0 else 1.0

        for i, (name, value) in enumerate(values.items()):
            deviation = abs(value - ensemble_mean) / denom
            score = max(0.0, min(1.0, 1.0 - deviation))
            self.model_scores[name] = score

            color = _MODEL_COLORS.get(name, _FALLBACK_PALETTE[i % len(_FALLBACK_PALETTE)])
            row = QHBoxLayout()
            row.setSpacing(10)
            name_label = QLabel(name)
            name_label.setStyleSheet(label_style("text_secondary", "xs", "bold"))
            name_label.setFixedWidth(64)
            row.addWidget(name_label)

            bar = HorizontalBarGauge(color)
            bar.set_fraction(score)
            row.addWidget(bar, stretch=1)

            value_label = QLabel(f"{score:.2f}")
            value_label.setStyleSheet(label_style("text_primary", "xs", "bold"))
            value_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            row.addWidget(value_label)

            self._rows_layout.addLayout(row)
            self._bars[name] = bar
            self._value_labels[name] = value_label

        overall = sum(self.model_scores.values()) / len(self.model_scores)
        if overall >= 0.75:
            verdict, color_token = "High Agreement", "success"
        elif overall >= 0.5:
            verdict, color_token = "Moderate Agreement", "warning"
        else:
            verdict, color_token = "Low Agreement", "warning"
        self.verdict_label.setText(verdict)
        self.verdict_label.setStyleSheet(label_style(color_token, "xs", "bold"))
