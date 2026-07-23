from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QToolBar,
)

from acf.dashboard.manager import DashboardManager
from acf.gui.menu import MenuManager
from acf.workspace.manager import WorkspaceManager


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Workspace
        self.workspace = WorkspaceManager()

        # Fenêtre
        self.setWindowTitle("Atmospheric Complexity Framework")
        self.resize(1600, 900)

        # Menu
        self.menu = MenuManager(self)

        # Toolbar
        self._create_toolbar()

        # StatusBar
        self._create_statusbar()

        # Dashboard
        self.dashboard = DashboardManager(self)
        self.dashboard.initialize()

    ##################################################

    def _create_toolbar(self):

        toolbar = QToolBar("Main Toolbar")

        self.addToolBar(toolbar)

        toolbar.addAction("Open")
        toolbar.addAction("Save")
        toolbar.addAction("Run")
        toolbar.addAction("Stop")

    ##################################################

    def _create_statusbar(self):

        status = QStatusBar()

        status.showMessage("Ready")

        self.setStatusBar(status)
