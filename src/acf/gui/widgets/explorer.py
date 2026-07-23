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

        self.setHeaderLabel(
            "Workspace"
        )

        self.setAnimated(
            True
        )

        self.setAlternatingRowColors(
            True
        )



    ################################################


    def load_project(self, project):

        self.clear()


        if project is None:

            return



        root = QTreeWidgetItem(
            [
                project.name
            ]
        )


        self.addTopLevelItem(
            root
        )


        self.populate(
            root,
            project.root_path
        )


        root.setExpanded(
            True
        )



    ################################################


    def populate(self,parent,path):

        path = Path(path)


        if not path.exists():

            return



        for item in sorted(
            path.iterdir()
        ):


            node = QTreeWidgetItem(
                [
                    item.name
                ]
            )


            parent.addChild(
                node
            )


            if item.is_dir():

                self.populate(
                    node,
                    item
                )



    ################################################
    # DATASETS
    ################################################


    def refresh_datasets(
        self,
        datasets
    ):


        dataset_root = QTreeWidgetItem(
            [
                "🌦 Datasets"
            ]
        )


        self.addTopLevelItem(
            dataset_root
        )



        for dataset in datasets:


            node = QTreeWidgetItem(
                [
                    dataset.name
                ]
            )


            dataset_root.addChild(
                node
            )



            variables = QTreeWidgetItem(
                [
                    "Variables"
                ]
            )


            node.addChild(
                variables
            )



            for var in dataset.variable_names:


                variables.addChild(
                    QTreeWidgetItem(
                        [
                            var
                        ]
                    )
                )



            metadata = QTreeWidgetItem(
                [
                    "Metadata"
                ]
            )


            node.addChild(
                metadata
            )


            dimensions = QTreeWidgetItem(
                [
                    "Dimensions"
                ]
            )


            node.addChild(
                dimensions
            )



        dataset_root.setExpanded(
            True
        )
