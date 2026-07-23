"""
ACF Explorer Widget

Projet + Datasets scientifiques
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


        self.setAnimated(True)

        self.setAlternatingRowColors(True)



    ##################################################

    def load_project(self, project):


        self.clear()


        if project is None:

            return



        root = QTreeWidgetItem(
            [
                "🌎 " + project.name
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



    ##################################################

    def populate(
        self,
        parent,
        path
    ):


        path = Path(path)


        if not path.exists():

            return



        for item in sorted(
            path.iterdir(),
            key=lambda x: (
                x.is_file(),
                x.name.lower()
            )
        ):


            if item.is_dir():


                node = QTreeWidgetItem(
                    [
                        "📁 " + item.name
                    ]
                )


                parent.addChild(
                    node
                )


                self.populate(
                    node,
                    item
                )


            else:


                node = QTreeWidgetItem(
                    [
                        "📄 " + item.name
                    ]
                )


                parent.addChild(
                    node
                )



    ##################################################

    def load_datasets(
        self,
        datasets
    ):


        if not datasets:

            return



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
                    "📊 " + dataset.name
                ]
            )


            dataset_root.addChild(
                node
            )



            info = QTreeWidgetItem(
                [
                    "Type : " + dataset.filetype
                ]
            )


            node.addChild(
                info
            )



            variables = QTreeWidgetItem(
                [
                    "Variables"
                ]
            )


            node.addChild(
                variables
            )



            for variable in dataset.variable_names:


                var_node = QTreeWidgetItem(
                    [
                        "🔹 " + variable
                    ]
                )


                variables.addChild(
                    var_node
                )



            node.setExpanded(
                True
            )


        dataset_root.setExpanded(
            True
        )



    ##################################################

    def clear_project(self):

        self.clear()
