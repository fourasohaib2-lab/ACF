"""
Atmospheric Complexity Framework (ACF)

Dataset Panel
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
)


class DatasetPanel(QDockWidget):
    """
    Dock widget displaying loaded scientific datasets.
    """

    def __init__(self, parent=None):

        super().__init__("Datasets", parent)

        self.data_manager = None

        self.tree = None

        self.build_ui()

    ##################################################

    def build_ui(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel("Loaded Datasets")

        self.tree.setAlternatingRowColors(True)

        self.tree.setRootIsDecorated(True)

        layout.addWidget(self.tree)

        self.setWidget(widget)

    ##################################################

    def set_data_manager(self, manager):

        self.data_manager = manager

        self.refresh()

    ##################################################

    def refresh(self):

        self.tree.clear()

        if self.data_manager is None:
            return

        registry = getattr(
            self.data_manager,
            "registry",
            None,
        )

        if registry is None:
            return

        datasets = getattr(
            registry,
            "datasets",
            [],
        )

        #
        # Supporte :
        #
        # registry.datasets      -> liste
        # registry.datasets()    -> méthode
        #
        if callable(datasets):
            datasets = datasets()

        for dataset in datasets:

            dataset_item = QTreeWidgetItem(self.tree)

            dataset_name = getattr(
                dataset,
                "name",
                "Unnamed Dataset",
            )

            dataset_item.setText(
                0,
                dataset_name,
            )

            dataset_item.setData(
                0,
                Qt.UserRole,
                dataset,
            )

            variables = getattr(
                dataset,
                "variables",
                [],
            )

            for variable in variables:

                variable_item = QTreeWidgetItem(
                    dataset_item
                )

                variable_item.setText(
                    0,
                    str(variable),
                )

                variable_item.setData(
                    0,
                    Qt.UserRole,
                    variable,
                )

        self.tree.expandAll()

    ##################################################

    def clear(self):

        self.tree.clear()

    ##################################################

    def selected_item(self):

        items = self.tree.selectedItems()

        if not items:
            return None

        return items[0].data(
            0,
            Qt.UserRole,
        )

    ##################################################

    def dataset_count(self):

        return self.tree.topLevelItemCount()
