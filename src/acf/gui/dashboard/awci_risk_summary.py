"""
AWCI Risk Summary Panel
=======================

Small badge list (Turbulence / Icing / Convective / Overall / Physical /
Forecast) matching the reference mockup's "RISK SUMMARY" panel. Levels are
derived from the real AWCICalculator module scores for the route's worst
point, not invented independently of the AWCI computation.

Physical / Forecast rows (added 2026-09-02, docs/
ACF_ARCHITECTURE_TARGET_GAP_MAP.md's Complexity Engine layer 17): the
target dashboard mockup shows Composite/Physical/Forecast as three
distinct numbers, not one blended score. `AWCICalculator.calculate()`
now returns `physical_score`/`forecast_score` alongside `awci`
(calculator.py's own docstring has the full rationale) - these two rows
surface that split. Either can legitimately be `None` (undefined
renormalization, e.g. a caller zeroed a whole dimension's weights); the
row then shows "—", never a fabricated score.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import risk_qcolor

_ROWS = [
    ("turbulence", "🌪️", "Turbulence Risk", "dynamic"),
    ("icing", "❄️", "Icing Risk", "microphysical"),
    ("convective", "⛈️", "Convective Risk", "convective"),
    ("overall", "📊", "Overall Complexity", None),
    ("physical", "🌡️", "Physical Complexity", "__physical__"),
    ("forecast", "🎯", "Forecast Complexity", "__forecast__"),
]

_BANDS = [(0, "Low"), (35, "Moderate"), (50, "High"), (65, "Very High"), (85, "Extreme")]


def _band(score: float) -> str:
    level = _BANDS[0][1]
    for threshold, name in _BANDS:
        if score >= threshold:
            level = name
    return level


class AWCIRiskSummary(QWidget):
    """Titled risk-badge panel."""

    def __init__(self, title: str = "RISK SUMMARY", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self.setStyleSheet("background-color: #16213e; border: 1px solid #263450; border-radius: 6px;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(6)

        header = QLabel(title)
        header.setStyleSheet("color: #e8edf5; font-size: 11px; font-weight: bold; border: none;")
        outer.addWidget(header)

        self._rows: dict[str, tuple[QLabel, QLabel]] = {}
        for key, icon, label, _module in _ROWS:
            row = QFrame()
            row.setStyleSheet("border: none;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)

            lbl = QLabel(f"{icon}  {label}")
            lbl.setStyleSheet("color: #9fb0c9; font-size: 10px; border: none;")
            row_layout.addWidget(lbl)
            row_layout.addStretch()

            badge = QLabel("—")
            badge.setStyleSheet("color: #6b7a94; font-size: 10px; font-weight: bold; border: none;")
            row_layout.addWidget(badge)

            outer.addWidget(row)
            self._rows[key] = (lbl, badge)

    def update_data(
        self,
        module_scores: dict[str, float],
        overall_awci: float,
        physical_score: float | None = None,
        forecast_score: float | None = None,
    ) -> None:
        specials = {"__physical__": physical_score, "__forecast__": forecast_score}
        for key, _icon, _label, module in _ROWS:
            _lbl, badge = self._rows[key]

            if module is None:
                score: float | None = overall_awci
            elif module in specials:
                score = specials[module]
            else:
                score = module_scores.get(module, 0.0)

            if score is None:
                badge.setText("—")
                badge.setStyleSheet("color: #6b7a94; font-size: 10px; font-weight: bold; border: none;")
                continue

            level = _band(score)
            color = risk_qcolor(level)
            badge.setText(level)
            badge.setStyleSheet(
                f"color: rgb({color.red()},{color.green()},{color.blue()}); "
                "font-size: 10px; font-weight: bold; border: none;"
            )
