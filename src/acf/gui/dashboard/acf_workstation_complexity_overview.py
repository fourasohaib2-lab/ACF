"""
ACF Scientific Workstation — Complexity Overview
====================================================

Matches acf_workstation_reference.jpg's single "Complexity Overview"
gauge plus its 8-factor breakdown list (Instability/Moisture/Shear/
Convection/Gradients/Vertical Structure/Temporal Evolution/Model
Disagreement).

Honesty note: the previous ("core-only") ACF Workstation deliberately
never combined complexity dimensions into one score, to avoid an
arbitrarily-fabricated composite. This panel DOES show one gauge, per
the new reference image - but it is nothing more than the plain
arithmetic mean of the real per-dimension values passed in via
`update_from_factors()` (any factor whose real value is `None` -
"not computed" - is excluded from the mean, not treated as 0). It is
not an independently-modeled or ML-derived score.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

_FACTOR_ORDER = [
    "Instability", "Moisture", "Shear", "Convection",
    "Gradients", "Vertical Structure", "Temporal Evolution", "Model Disagreement",
]


def _level_for(score: float) -> str:
    if score >= 0.65:
        return "High"
    if score >= 0.35:
        return "Moderate"
    return "Low"


class ComplexityOverviewPanel(QWidget):
    """Real, disclosed-mean Complexity Overview gauge."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.composite_score: float | None = None

        outer = QVBoxLayout(self)
        self.gauge_label = QLabel("NOT_COMPUTED")
        self.gauge_label.setStyleSheet(label_style("text_primary", "xl"))
        outer.addWidget(self.gauge_label)

        self.factor_grid = QGridLayout()
        outer.addLayout(self.factor_grid)
        self._factor_labels: dict[str, QLabel] = {}
        for row, name in enumerate(_FACTOR_ORDER):
            heading = QLabel(name)
            heading.setStyleSheet(label_style("text_muted", "xs"))
            value = QLabel("NOT_COMPUTED")
            self.factor_grid.addWidget(heading, row, 0)
            self.factor_grid.addWidget(value, row, 1)
            self._factor_labels[name] = value

    def update_from_factors(self, factors: dict[str, float | None]) -> None:
        """Real display of each real per-dimension value, plus their
        disclosed arithmetic mean (None values excluded, not zeroed)."""
        for name, label in self._factor_labels.items():
            value = factors.get(name)
            label.setText(f"{value:.2f}" if value is not None else "NOT_COMPUTED")

        real_values = [v for v in factors.values() if v is not None]
        if not real_values:
            self.composite_score = None
            self.gauge_label.setText("NOT_COMPUTED")
            return

        self.composite_score = sum(real_values) / len(real_values)
        self.gauge_label.setText(f"{self.composite_score:.2f} {_level_for(self.composite_score)}")
