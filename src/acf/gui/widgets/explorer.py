from PySide6.QtWidgets import QListWidget

class ExplorerWidget(QListWidget):

    def __init__(self):
        super().__init__()

        self.addItems([
            "Project",
            "Workspace",
            "Datasets",
            "Maps",
            "Models",
            "Plugins",
            "Reports"
        ])
