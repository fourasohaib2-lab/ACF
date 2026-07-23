from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt


class TimelinePanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("⏱ Timeline"))

        slider = QSlider(Qt.Horizontal)

        slider.setMinimum(0)
        slider.setMaximum(100)

        layout.addWidget(slider)
