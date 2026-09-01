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

    NOTE (found, NOT changed - Physics Guard): add_button/remove_button/
    up_button/down_button/opacity_slider are created here but never
    connected to any handler, neither in this class nor by
    gui.main_window.MainWindow (the only real instantiator, verified
    via grep) - in the live app, clicking +/-/up/down or moving the
    opacity slider currently does nothing. self.layer_tree (LayerTree)
    does have genuine add_layer()/remove_layer() methods that COULD
    back +/-, but MainWindow never calls them either (this panel is
    never populated with real layers, and is entirely disconnected from
    the app's real layer manager in gui.map.layers.layer_manager).
    Reordering (up/down) has no backing capability anywhere in
    LayerTree at all. Not fixed here: wiring this up would mean
    inventing the intended UI flow (e.g. what "+" should prompt for)
    and how this panel should connect to the real layer manager,
    neither of which has an existing spec to implement against -
    flagged rather than fabricated, same principle as
    hpc_workflow.workflow_validator's own NOTE.
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
