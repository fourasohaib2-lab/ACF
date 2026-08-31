"""
Atmospheric Complexity Framework (ACF)

Layer Panel
===========

Professional layer manager.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class LayerPanel(QDockWidget):
    """
    Layer management panel.
    """

    def __init__(self, parent=None):

        super().__init__("Layers", parent)

        self.layer_manager = None
        self.tree: QTreeWidget | None = None

        self._build_ui()

    ##################################################

    def _build_ui(self):

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(4, 4, 4, 4)

        self.tree = QTreeWidget()

        self.tree.setHeaderHidden(True)

        self.tree.setAlternatingRowColors(True)

        self.tree.itemChanged.connect(self._item_changed)

        self.tree.currentItemChanged.connect(self._current_item_changed)
        layout.addWidget(self.tree)

        self.setWidget(container)

    ##################################################

    def set_layer_manager(self, manager):

        if self.layer_manager is manager:
            return

        self.layer_manager = manager

        if self.layer_manager is None:
            return

        self.layer_manager.layerAdded.connect(self._on_layer_added)

        self.layer_manager.layerRemoved.connect(self._on_layer_removed)

        self.layer_manager.layerChanged.connect(self._on_layer_changed)

        self.layer_manager.layersCleared.connect(self.refresh)

        self.layer_manager.currentLayerChanged.connect(self._on_current_layer_changed)

        self.refresh()

    ##################################################

    def refresh(self):

        if self.tree is None:
            return

        self.tree.clear()

        if self.layer_manager is None:
            return

        meteorology = QTreeWidgetItem(self.tree, ["Meteorology"])
        QTreeWidgetItem(self.tree, ["Satellite"])
        QTreeWidgetItem(self.tree, ["Radar"])
        QTreeWidgetItem(self.tree, ["Ocean"])
        QTreeWidgetItem(self.tree, ["Terrain"])
        for layer in self.layer_manager.layers():
            item = QTreeWidgetItem(meteorology, [layer.name])

            item.setData(0, Qt.ItemDataRole.UserRole, layer.id)

            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)

            if layer.visible:
                item.setCheckState(0, Qt.CheckState.Checked)

            else:
                item.setCheckState(0, Qt.CheckState.Unchecked)

        self.tree.expandAll()

    ##################################################

    def selected_layer(self):

        if self.tree is None:
            return None

        item = self.tree.currentItem()

        if item is None:
            return None

        return item.data(0, Qt.ItemDataRole.UserRole)

    ##################################################

    def _item_changed(self, item, column):

        if self.layer_manager is None:
            return

        layer_id = item.data(0, Qt.ItemDataRole.UserRole)

        if layer_id is None:
            return

        if item.checkState(0) == Qt.CheckState.Checked:
            self.layer_manager.show_layer(layer_id)

        else:
            self.layer_manager.hide_layer(layer_id)

    ##################################################

    def _current_item_changed(
        self,
        current,
        previous,
    ):

        if self.layer_manager is None:
            return

        if current is None:
            return

        layer_id = current.data(0, Qt.UserRole)

        if layer_id is None:
            return

        self.layer_manager.set_current_layer(layer_id)

    ##################################################

    def _on_layer_added(self, layer):

        self.refresh()

    ##################################################

    def _on_layer_removed(self, layer_id):

        self.refresh()

    ##################################################

    def _on_layer_changed(self, layer):

        self.refresh()

    ##################################################

    def _on_current_layer_changed(self, layer):

        if layer is None:
            self.tree.clearSelection()
            return

        self._select_layer(layer.id)

    ##################################################

    def _select_layer(self, layer_id):

        root = self.tree.invisibleRootItem()

        stack = [root]

        while stack:
            parent = stack.pop()

            for i in range(parent.childCount()):
                child = parent.child(i)

                if child.data(0, Qt.UserRole) == layer_id:
                    self.tree.setCurrentItem(child)

                    return

                stack.append(child)
