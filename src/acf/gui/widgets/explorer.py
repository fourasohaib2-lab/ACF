"""
ACF Explorer
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
)


class ExplorerWidget(QTreeWidget):
    def __init__(self):

        super().__init__()

        self.setHeaderLabel("Workspace")

        self.setAnimated(True)

        self.setAlternatingRowColors(True)

    ################################################

    def load_project(self, project):

        self.clear()

        if project is None:
            return

        root = QTreeWidgetItem([project.name])

        self.addTopLevelItem(root)

        self.populate(root, project.root_path)

        root.setExpanded(True)

    ################################################

    def populate(self, parent, path):

        path = Path(path)

        if not path.exists():
            return

        for item in sorted(path.iterdir()):
            node = QTreeWidgetItem([item.name])

            parent.addChild(node)

            if item.is_dir():
                self.populate(node, item)

    ################################################
    # DATASETS
    ################################################

    def refresh_datasets(self, datasets):
        """
        NOTE (correction, 2026-09-07 - real bug, found by an end-to-end
        smoke test of ClassicDashboardWindow's File/Data menu, not a
        code read): this used to unconditionally addTopLevelItem() a
        new "Datasets" branch on every call with no removal of any
        prior one. MenuManager.refresh_dataset_view() (the only real
        caller) runs this every time a dataset is opened/refreshed -
        a completely ordinary session opening 2-3 datasets left 2-3
        duplicate "Datasets" branches stacked in the tree, confirmed by
        a direct test (topLevelItemCount() grew 1,2,3,4... across 4
        calls instead of staying at 1). Fixed by removing any existing
        "Datasets" branch first - deliberately not a blanket clear()
        the way load_project() uses, since that would also wipe a
        project tree already loaded above it.
        """

        for index in reversed(range(self.topLevelItemCount())):
            if self.topLevelItem(index).text(0) == "🌦 Datasets":
                self.takeTopLevelItem(index)

        dataset_root = QTreeWidgetItem(["🌦 Datasets"])

        self.addTopLevelItem(dataset_root)

        for dataset in datasets:
            node = QTreeWidgetItem([dataset.name])

            dataset_root.addChild(node)

            variables = QTreeWidgetItem(["Variables"])

            node.addChild(variables)

            for var in dataset.variable_names:
                variables.addChild(QTreeWidgetItem([var]))

            metadata = QTreeWidgetItem(["Metadata"])

            node.addChild(metadata)

            dimensions = QTreeWidgetItem(["Dimensions"])

            node.addChild(dimensions)

        dataset_root.setExpanded(True)
