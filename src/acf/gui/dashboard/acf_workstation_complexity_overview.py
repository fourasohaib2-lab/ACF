"""
ACF Scientific Workstation — Complexity Overview
====================================================

Matches acf_workstation_reference.jpg's "Complexity Overview" card: a
circular ring gauge on the left with the composite score/level, and its
8-factor breakdown list (colored dot + name + value) on the right.

Honesty note: the previous ("core-only") ACF Workstation deliberately
never combined complexity dimensions into one score, to avoid an
arbitrarily-fabricated composite. This panel DOES show one gauge, per
the new reference image - but it is nothing more than the plain
arithmetic mean of the real per-dimension values passed in via
`update_from_factors()` (any factor whose real value is `None` -
"not computed" - is excluded from the mean, not treated as 0). It is
not an independently-modeled or ML-derived score. The gauge's own
tooltip discloses its denominator (e.g. "mean of 6 of 8 real factors"),
so a viewer never mistakes a mean of a handful of real factors for a
complete 8-factor score.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget

from acf.gui.dashboard.acf_workstation_gauges import CircularGaugeWidget, ColorDot
from acf.gui.theme_tokens import label_style

#: (factor name, legend dot color) - colors chosen to visually match
#: acf_workstation_reference.jpg's own Complexity Overview dot legend,
#: not a scientific encoding of severity.
_FACTOR_ORDER: list[tuple[str, str]] = [
    ("Instability", "#ef4444"),
    ("Moisture", "#f97316"),
    ("Shear", "#22c55e"),
    ("Convection", "#eab308"),
    ("Gradients", "#3b82f6"),
    ("Vertical Structure", "#6366f1"),
    ("Temporal Evolution", "#0ea5e9"),
    ("Model Disagreement", "#ec4899"),
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

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        self.gauge = CircularGaugeWidget()
        outer.addWidget(self.gauge)

        self.factor_grid = QGridLayout()
        self.factor_grid.setHorizontalSpacing(8)
        self.factor_grid.setVerticalSpacing(6)
        outer.addLayout(self.factor_grid, stretch=1)

        self._factor_labels: dict[str, QLabel] = {}
        for row, (name, color) in enumerate(_FACTOR_ORDER):
            self.factor_grid.addWidget(ColorDot(color), row, 0)
            heading = QLabel(name)
            heading.setStyleSheet(label_style("text_secondary", "xs"))
            self.factor_grid.addWidget(heading, row, 1)
            value = QLabel("NOT_COMPUTED")
            value.setStyleSheet(label_style("text_primary", "xs", "bold"))
            self.factor_grid.addWidget(value, row, 2)
            self._factor_labels[name] = value
        self.factor_grid.setColumnStretch(1, 1)

        # Kept for tests/back-compat: a plain text label mirroring the
        # gauge's own number/level/denominator, not shown in the layout
        # (the circular gauge paints that information now).
        self.gauge_label = QLabel("NOT_COMPUTED")
        self.gauge_label.hide()

    def update_from_factors(self, factors: dict[str, float | None]) -> None:
        """Real display of each real per-dimension value, plus their
        disclosed arithmetic mean (None values excluded, not zeroed)."""
        for name, label in self._factor_labels.items():
            value = factors.get(name)
            label.setText(f"{value:.2f}" if value is not None else "NOT_COMPUTED")

        real_values = [v for v in factors.values() if v is not None]
        if not real_values:
            self.composite_score = None
            self.gauge.set_value(None, "NOT_COMPUTED")
            self.gauge.setToolTip("NOT_COMPUTED - no real factors available")
            self.gauge_label.setText("NOT_COMPUTED")
            return

        self.composite_score = sum(real_values) / len(real_values)
        level = _level_for(self.composite_score)
        self.gauge.set_value(self.composite_score, level)
        self.gauge.setToolTip(f"Mean of {len(real_values)} of {len(factors)} real factors")
        self.gauge_label.setText(
            f"{self.composite_score:.2f} {level} (mean of {len(real_values)} of {len(factors)} real factors)"
        )
