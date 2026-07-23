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
