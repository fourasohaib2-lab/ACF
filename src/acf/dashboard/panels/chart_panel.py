"""
Atmospheric Complexity Framework (ACF)

DASHBOARD - Chart Panel

Purpose:
--------
Provides Chart Panel functionality for the ACF framework.

Responsibilities:
-----------------
• Manage chart panel logic and state representations.
• Integrate with the dashboard subsystem of the ACF scientific engine.

Major Components:
-----------------
• ChartPanel

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
    QWidget,
    QLabel,
    QVBoxLayout,
    QListWidget,
)


class ChartPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Scientific Charts")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        charts = QListWidget()

        charts.addItems([
            "Temperature",
            "Pressure",
            "Wind Speed",
            "Wind Direction",
            "Humidity",
            "Precipitation",
            "Cloud Cover",
            "CAPE",
            "CIN",
            "Lifted Index",
            "Skew-T",
            "Time Series",
        ])

        layout.addWidget(title)
        layout.addWidget(charts)
