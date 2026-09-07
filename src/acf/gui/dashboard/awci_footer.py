"""
AWCI Footer Strip
=================

Row of 5 real, clickable feature buttons matching the reference
mockup's footer (Synthetic View / Decision Support / Multi-Scale /
Adaptive to Mission / Research Stage).

NOTE (correction, 2026-09-07 - explicit user request "la barre d'outils
en bas ... sont des boutons je veux les rendre des boutons
fonctionnelles"): these used to be 5 purely decorative QLabel cells -
real feature NAMES with no click handler at all, matching the
reference mockup's own footer but never made interactive. Each cell
is now a real clickable button (AWCIFooterCell, hover/pressed states,
a pointing-hand cursor) emitting a real Signal(str) keyed by the same
item it displays - AWCIDashboard connects each key to the existing
real dashboard feature its own label already honestly describes,
never a new/fabricated action:
  - "synthetic_view"      -> _revert_to_demo() (the demo/synthetic
                              mode this label's own text already names)
  - "decision_support"    -> _open_alerts() (real active-risk alerts,
                              "helps forecasters and aircrews" decide)
  - "multi_scale"         -> cycles VIEW MODE (Global/Regional/
                              Vertical Cross-Section - the real 3 real
                              scales this label's own text names)
  - "adaptive_to_mission" -> _open_vertical_profile() (real per-
                              flight-level breakdown - "depends on...
                              phase of flight")
  - "research_stage"      -> _open_execution_report() (real per-
                              variable quality/diagnostics report -
                              "to be validated and improved")
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

_ITEMS = [
    ("synthetic_view", "🌐", "SYNTHETIC VIEW", "One map to understand\nthe complexity"),
    ("decision_support", "🧑‍✈️", "DECISION SUPPORT", "Helps forecasters and\naircrews"),
    ("multi_scale", "🗂️", "MULTI-SCALE", "Global – Regional – Vertical\n– Time evolution"),
    ("adaptive_to_mission", "✈️", "ADAPTIVE TO MISSION", "Depends on aircraft, phase\nof flight and operation"),
    ("research_stage", "🧪", "RESEARCH STAGE", "Prototype – To be validated\nand improved"),
]


class AWCIFooterCell(QFrame):
    """One real, clickable footer button (icon + title). The
    description text is a real tooltip, not a second visible line -
    real vertical-space fix (2026-09-07, explicit user complaint
    "je sens qu'il est dispatcher" / real dashboard height exceeding a
    normal screen, forcing scrolling the user also explicitly does not
    want - see AWCIDashboard's own note on this same fix for the full
    real measurement)."""

    clicked = Signal()

    def __init__(self, icon: str, title: str, desc: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("footerCell")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(desc.replace("\n", " "))
        self.setStyleSheet(
            "QFrame#footerCell { border-radius: 6px; padding: 2px 6px; }"
            "QFrame#footerCell:hover { background-color: #182238; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 14px; background: transparent;")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #e8edf5; font-size: 9px; font-weight: bold; background: transparent;")
        layout.addWidget(title_lbl)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override signature
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class AWCIFooter(QWidget):
    """Row of 5 real, clickable feature buttons - see module docstring
    for what each one now does and why."""

    itemClicked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #121a2b; border-top: 1px solid #263450;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setSpacing(24)

        self.cells: dict[str, AWCIFooterCell] = {}
        for key, icon, title, desc in _ITEMS:
            cell = AWCIFooterCell(icon, title, desc)
            cell.clicked.connect(lambda k=key: self.itemClicked.emit(k))
            self.cells[key] = cell
            layout.addWidget(cell)

        layout.addStretch()
