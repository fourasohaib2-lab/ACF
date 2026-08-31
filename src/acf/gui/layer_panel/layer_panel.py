"""
Atmospheric Complexity Framework (ACF)

Layer Panel
===========

Professional layer management panel.
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

from .layer_tree import LayerTree


class LayerPanel(QWidget):
    """
    Professional layer panel.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.layer_tree = LayerTree()

        self.build_ui()

    ##################################################

    def build_ui(self):

        layout = QVBoxLayout()

        ##################################################
        # Title
        ##################################################

        title = QLabel("Layers")

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title.setStyleSheet(
            """
            QLabel{
                font-size:16px;
                font-weight:bold;
            }
            """
        )

        layout.addWidget(title)

        ##################################################
        # Layer Tree
        ##################################################

        layout.addWidget(self.layer_tree)

        ##################################################
        # Buttons
        ##################################################

        buttons = QHBoxLayout()

        self.add_button = QPushButton("+")

        self.remove_button = QPushButton("-")

        self.up_button = QPushButton("↑")

        self.down_button = QPushButton("↓")

        buttons.addWidget(self.add_button)

        buttons.addWidget(self.remove_button)

        buttons.addWidget(self.up_button)

        buttons.addWidget(self.down_button)

        layout.addLayout(buttons)

        ##################################################
        # Opacity
        ##################################################

        layout.addWidget(QLabel("Opacity"))

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)

        self.opacity_slider.setRange(0, 100)

        self.opacity_slider.setValue(100)

        layout.addWidget(self.opacity_slider)

        self.setLayout(layout)

    ##################################################

    def tree(self):

        return self.layer_tree
