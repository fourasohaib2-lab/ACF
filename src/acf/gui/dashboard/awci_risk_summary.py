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

Clickable rows (added 2026-09-03, docs/awci/AWCI_UI_AUDIT.md /
AWCI_INTERACTION_MATRIX.md - the pre-implementation audit found these
badges were purely decorative, matching the same "dead UI" gap the
radar's own component list had before it was made clickable). Reuses
that exact same real click pattern (a QFrame + mousePressEvent(), not a
QPushButton, to keep this row's original icon-left/badge-right layout
unchanged) - see _ComponentValueList/_ComponentRow in awci_dashboard.py
for the earlier, now-duplicated convention this mirrors.
"""

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import risk_qcolor
from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet, label_style

#: Real module-score breakdown shown by AWCIRiskBadgeDetailDialog for
#: the 3 composite rows (overall/physical/forecast) - the first 7 keys
#: match _ComponentValueList's own visible list (awci_dashboard.py,
#: which deliberately stays at 7 rows to match the reference mockup's
#: own "AWCI COMPONENTS" list pixel-for-pixel - not extended here).
#: ensemble_spread/model_disagreement (added 2026-09-03, found while
#: closing §51's vertical-profile detail dialog - the same 2 real
#: AWCICalculator.calculate_module_scores() keys were missing there
#: too) have no fixed-layout mockup constraint on this popup, so they
#: are shown here for real completeness - honestly ~0.0 in demo mode
#: (this dashboard's own per-point pipeline never supplies real
#: ensemble_members/model_realizations), never a fabricated non-zero
#: value.
_MODULE_LABELS = [
    ("dynamic", "🌀", "Dynamic"),
    ("thermodynamic", "🌡️", "Thermodynamic"),
    ("convective", "⛈️", "Convective"),
    ("microphysical", "❄️", "Microphysical"),
    ("topographic", "⛰️", "Topographic"),
    ("temporal", "🕐", "Temporal"),
    ("confidence", "❓", "Uncertainty"),
    ("ensemble_spread", "📊", "Ensemble spread"),
    ("model_disagreement", "🔀", "Model disagreement"),
]

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


class _RiskRow(QFrame):
    """One real, clickable risk-badge row - see module docstring for why
    this mirrors _ComponentRow (awci_dashboard.py) rather than importing
    that module-private class across modules."""

    clicked = Signal(str)

    def __init__(self, key: str, icon: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._key = key
        self._base_style = "border: none; border-radius: 4px;"
        self._hover_style = f"border: none; border-radius: 4px; background-color: {TOKENS.bg_surface_alt};"
        self.setStyleSheet(self._base_style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Click for the real detail behind {label}.")

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(f"{icon}  {label}")
        self.label.setStyleSheet("color: #9fb0c9; font-size: 10px; border: none;")
        row_layout.addWidget(self.label)
        row_layout.addStretch()

        self.badge = QLabel("—")
        self.badge.setStyleSheet("color: #6b7a94; font-size: 10px; font-weight: bold; border: none;")
        row_layout.addWidget(self.badge)

    def mousePressEvent(self, event: Any) -> None:
        self.clicked.emit(self._key)
        super().mousePressEvent(event)

    def enterEvent(self, event: Any) -> None:
        self.setStyleSheet(self._hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        self.setStyleSheet(self._base_style)
        super().leaveEvent(event)


class AWCIRiskSummary(QWidget):
    """Titled risk-badge panel."""

    #: Real click-to-detail signal (added 2026-09-03, see module
    #: docstring) - key is one of _ROWS' own first elements
    #: ("turbulence"/"icing"/"convective"/"overall"/"physical"/
    #: "forecast"), the exact real row clicked.
    rowClicked = Signal(str)

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
            row = _RiskRow(key, icon, label)
            row.clicked.connect(self.rowClicked)
            outer.addWidget(row)
            self._rows[key] = (row.label, row.badge)

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


class AWCIRiskBadgeDetailDialog(QDialog):
    """Real detail popup for the 3 composite risk badges (overall/
    physical/forecast - see module docstring). The other 3 rows
    (turbulence/icing/convective) map onto a real AWCICalculator module
    and reuse the existing AWCIComponentDetailDialog instead (see
    AWCIDashboard._on_risk_badge_clicked()) - this dialog exists only
    for the 3 rows that have no single module formula of their own.
    Shows the real module_scores breakdown that composes the clicked
    number - the same real values AWCIRiskSummary.update_data() itself
    was just called with, never a fabricated derivation."""

    _TITLES = {"overall": "Overall Complexity", "physical": "Physical Complexity", "forecast": "Forecast Complexity"}

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(dashboard_stylesheet())
        layout = QVBoxLayout(self)
        self._title_label = QLabel()
        self._title_label.setStyleSheet(label_style("text_primary", "lg", "bold"))
        layout.addWidget(self._title_label)

        self._score_label = QLabel()
        self._score_label.setStyleSheet(label_style("text_primary", "md", "bold"))
        layout.addWidget(self._score_label)

        breakdown_header = QLabel("Real module-score breakdown (this point of interest):")
        breakdown_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        layout.addWidget(breakdown_header)

        self._module_rows: dict[str, QLabel] = {}
        for module_key, icon, label in _MODULE_LABELS:
            row = QLabel()
            row.setStyleSheet(label_style("text_secondary", "sm"))
            layout.addWidget(row)
            self._module_rows[module_key] = row

    def show_detail(
        self,
        key: str,
        module_scores: dict[str, float],
        overall_awci: float,
        physical_score: float | None,
        forecast_score: float | None,
    ) -> None:
        title = self._TITLES.get(key, key.title())
        self.setWindowTitle(f"AWCI – {title}")
        self._title_label.setText(title)

        score = {"overall": overall_awci, "physical": physical_score, "forecast": forecast_score}.get(key)
        if score is None:
            # A real, legitimately undefined renormalization (e.g. a
            # caller zeroed a whole dimension's weights) - never a
            # fabricated stand-in score, matching the badge itself
            # showing "—" for this same case (see update_data() above).
            self._score_label.setText("Score: — (undefined renormalization)")
        else:
            self._score_label.setText(f"Score: {score:.1f} / 100 ({_band(score)})")

        for module_key, icon, label in _MODULE_LABELS:
            value = module_scores.get(module_key)
            value_text = f"{value:.1f}" if value is not None else "—"
            self._module_rows[module_key].setText(f"{icon}  {label}: {value_text}")

        self.show()
        self.raise_()
        self.activateWindow()
