"""
Atmospheric Complexity Framework (ACF)

Property Panel
==============

Displays the properties of the selected layer.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFormLayout,
    QVBoxLayout,
    QFrame,
)


class PropertyPanel(QWidget):
    """
    Professional property panel.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.build_ui()

    ##################################################

    def build_ui(self):

        layout = QVBoxLayout()

        title = QLabel("Properties")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel{
                font-size:16px;
                font-weight:bold;
            }
        """)

        layout.addWidget(title)

        line = QFrame()

        line.setFrameShape(QFrame.HLine)

        layout.addWidget(line)

        form = QFormLayout()

        self.layer_name = QLabel("--")

        self.layer_type = QLabel("--")

        self.layer_visible = QLabel("--")

        self.layer_opacity = QLabel("--")

        form.addRow("Layer :", self.layer_name)

        form.addRow("Type :", self.layer_type)

        form.addRow("Visible :", self.layer_visible)

        form.addRow("Opacity :", self.layer_opacity)

        layout.addLayout(form)

        layout.addStretch()

        self.setLayout(layout)

    ##################################################

    def update_properties(self, layer):

        if layer is None:

            self.layer_name.setText("--")

            self.layer_type.setText("--")

            self.layer_visible.setText("--")

            self.layer_opacity.setText("--")

            return

        self.layer_name.setText(layer.name)

        self.layer_type.setText(layer.__class__.__name__)

        self.layer_visible.setText(str(layer.visible))

        self.layer_opacity.setText(f"{layer.opacity}%")

