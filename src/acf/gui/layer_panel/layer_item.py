"""
Atmospheric Complexity Framework (ACF)

Layer Item
==========

One graphical item representing a layer.
"""

from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QCheckBox,
)


class LayerItem(QWidget):
    """
    One layer inside the layer panel.
    """

    visibilityChanged = Signal(bool)

    ##################################################

    def __init__(
        self,
        layer_name="Layer",
        icon="🗺",
        visible=True,
        parent=None,
    ):

        super().__init__(parent)

        self.layer_name = layer_name

        self.icon = icon

        self.visible = visible

        self.build_ui()

    ##################################################

    def build_ui(self):

        layout = QHBoxLayout()

        layout.setContentsMargins(
            6,
            2,
            6,
            2,
        )

        self.checkbox = QCheckBox()

        self.checkbox.setChecked(
            self.visible
        )

        self.checkbox.toggled.connect(
            self.visibilityChanged.emit
        )

        self.icon_label = QLabel(self.icon)

        self.name_label = QLabel(
            self.layer_name
        )

        layout.addWidget(
            self.checkbox
        )

        layout.addWidget(
            self.icon_label
        )

        layout.addWidget(
            self.name_label
        )

        layout.addStretch()

        self.setLayout(layout)

    ##################################################

    def is_visible(self):

        return self.checkbox.isChecked()

    ##################################################

    def set_visible(
        self,
        value,
    ):

        self.checkbox.setChecked(value)

    ##################################################

    def name(self):

        return self.layer_name
