"""
Atmospheric Complexity Framework (ACF)

Layer Tree
==========

Professional layer tree widget.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from .layer_item import LayerItem


class LayerTree(QWidget):
    """
    Tree containing every layer.
    """

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.items = []

        self.layout = QVBoxLayout()

        self.layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )

        self.layout.setSpacing(2)

        self.layout.addStretch()

        self.setLayout(self.layout)

    ##################################################

    def add_layer(
        self,
        name,
        icon="🗺",
        visible=True,
    ):
        """
        Add one layer.
        """

        item = LayerItem(
            layer_name=name,
            icon=icon,
            visible=visible,
        )

        self.items.append(item)

        self.layout.insertWidget(
            self.layout.count() - 1,
            item,
        )

        return item

    ##################################################

    def remove_layer(self, name):
        """
        Remove a layer by name.
        """

        for item in self.items[:]:

            if item.name() == name:

                self.layout.removeWidget(item)

                item.deleteLater()

                self.items.remove(item)

                break

    ##################################################

    def clear(self):
        """
        Remove all layers.
        """

        for item in self.items:

            self.layout.removeWidget(item)

            item.deleteLater()

        self.items.clear()

    ##################################################

    def layer_names(self):

        return [
            item.name()
            for item in self.items
        ]

    ##################################################

    def count(self):

        return len(self.items)
