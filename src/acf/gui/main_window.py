"""
ACF Main Window

Fenêtre principale du logiciel
Atmospheric Complexity Framework
"""


from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QToolBar,
)

from acf.dashboard.manager import DashboardManager
from acf.gui.menu import MenuManager
from acf.workspace.manager import WorkspaceManager
from acf.data.manager import DataManager



class MainWindow(QMainWindow):


    def __init__(self):

        super().__init__()


        # Workspace

        self.workspace = WorkspaceManager()



        # Scientific Data

        self.data = DataManager()



        # Window

        self.setWindowTitle(
            "Atmospheric Complexity Framework"
        )

        self.resize(
            1600,
            900
        )



        # Dashboard

        self.dashboard = DashboardManager(
            self
        )

        self.dashboard.initialize()



        # Menu

        self.menu = MenuManager(
            self
        )



        # Toolbar

        self.create_toolbar()



        # Status

        self.create_statusbar()



    ################################################


    def create_toolbar(self):

        toolbar = QToolBar(
            "Main Toolbar"
        )

        self.addToolBar(
            toolbar
        )


        toolbar.addAction(
            "Open"
        )

        toolbar.addAction(
            "Save"
        )

        toolbar.addAction(
            "Run"
        )

        toolbar.addAction(
            "Stop"
        )



    ################################################


    def create_statusbar(self):

        status = QStatusBar()

        status.showMessage(
            "Ready"
        )

        self.setStatusBar(
            status
        )
