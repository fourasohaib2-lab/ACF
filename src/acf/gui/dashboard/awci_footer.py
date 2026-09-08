"""
AWCI Footer Strip
=================

Row of 5 labeled feature icons matching the reference mockup's footer
(Synthetic View / Decision Support / Multi-Scale / Adaptive to Mission /
Research Stage). Purely descriptive, like the reference's own footer.
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

_ITEMS = [
    ("🌐", "SYNTHETIC VIEW", "One map to understand\nthe complexity"),
    ("🧑‍✈️", "DECISION SUPPORT", "Helps forecasters and\naircrews"),
    ("🗂️", "MULTI-SCALE", "Global – Regional – Vertical\n– Time evolution"),
    ("✈️", "ADAPTIVE TO MISSION", "Depends on aircraft, phase\nof flight and operation"),
    ("🧪", "RESEARCH STAGE", "Prototype – To be validated\nand improved"),
]


class AWCIFooter(QWidget):
    """Static row of feature-explainer items."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #121a2b; border-top: 1px solid #263450;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(24)

        for icon, title, desc in _ITEMS:
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(8)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 18px;")
            cell_layout.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(0)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("color: #e8edf5; font-size: 9px; font-weight: bold;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color: #6b7a94; font-size: 8px;")
            text_col.addWidget(title_lbl)
            text_col.addWidget(desc_lbl)
            cell_layout.addLayout(text_col)

            layout.addWidget(cell)

        layout.addStretch()
