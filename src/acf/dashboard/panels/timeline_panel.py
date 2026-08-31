"""
Atmospheric Complexity Framework (ACF)

DASHBOARD - Timeline Panel

Purpose:
--------
Provides Timeline Panel functionality for the ACF framework.

Responsibilities:
-----------------
• Manage timeline panel logic and state representations.
• Integrate with the dashboard subsystem of the ACF scientific engine.

Major Components:
-----------------
• TimelinePanel

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.dashboard module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class TimelinePanel(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        title = QLabel("Timeline")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
        """)

        main_layout.addWidget(title)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)

        main_layout.addWidget(self.slider)

        buttons = QHBoxLayout()

        self.first_btn = QPushButton("⏮")
        self.prev_btn = QPushButton("◀")
        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.next_btn = QPushButton("▶")
        self.last_btn = QPushButton("⏭")

        buttons.addWidget(self.first_btn)
        buttons.addWidget(self.prev_btn)
        buttons.addWidget(self.play_btn)
        buttons.addWidget(self.pause_btn)
        buttons.addWidget(self.next_btn)
        buttons.addWidget(self.last_btn)

        main_layout.addLayout(buttons)

        self.info = QLabel("Forecast Hour : T+000")
        self.info.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self.info)
