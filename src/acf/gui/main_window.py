"""
Atmospheric Complexity Framework (ACF)

Main Window
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QToolBar,
)

from acf.dashboard.manager import DashboardManager
from acf.gui.menu import MenuManager

from acf.gui.map.map_canvas import MapCanvas

from acf.gui.docks.layer_panel import LayerPanel
from acf.gui.docks.dataset_panel import DatasetPanel

from acf.workspace.manager import WorkspaceManager
from acf.data.manager import DataManager

from acf.maps import VisualizationManager


class MainWindow(QMainWindow):
    """
    Main application window.
    """

    def __init__(self):

        super().__init__()

        ##################################################
        # Managers
        ##################################################

        self.workspace = WorkspaceManager()

        self.data = DataManager()

        self.visualization = VisualizationManager()

        self.visualization.initialize()

        ##################################################
        # Window
        ##################################################

        self.setWindowTitle(
            "Atmospheric Complexity Framework"
        )

        self.resize(
            1600,
            900,
        )

        ##################################################
        # Central Map Canvas
        ##################################################

        self.map_canvas = MapCanvas(self)

        self.map_canvas.set_visualization_manager(
            self.visualization
        )

        self.map_canvas.initialize()

        self.setCentralWidget(
            self.map_canvas
        )

        ##################################################
        # Dashboard
        ##################################################

        self.dashboard = DashboardManager(
            self
        )

        self.dashboard.initialize()

        ##################################################
        # Layer Panel
        ##################################################

        self.layer_panel = LayerPanel(self)

        self.layer_panel.set_layer_manager(
            self.visualization.layers()
        )

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.layer_panel,
        )

        ##################################################
        # Dataset Panel
        ##################################################

        self.dataset_panel = DatasetPanel(self)

        self.dataset_panel.set_data_manager(
            self.data
        )

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.dataset_panel,
        )

        ##################################################
        # Dock Tabs
        ##################################################

        self.tabifyDockWidget(
            self.layer_panel,
            self.dataset_panel,
        )

        self.layer_panel.raise_()

        ##################################################
        # Menu
        ##################################################

        self.menu = MenuManager(self)

        ##################################################
        # Toolbar
        ##################################################

        self.create_toolbar()

        ##################################################
        # Status Bar
        ##################################################

        self.create_statusbar()

    ##################################################

    def create_toolbar(self):

        toolbar = QToolBar(
            "Main Toolbar"
        )

        self.addToolBar(toolbar)

        toolbar.addAction("Open")

        toolbar.addAction("Save")

        toolbar.addSeparator()

        toolbar.addAction("Run")

        toolbar.addAction("Stop")

        toolbar.addSeparator()

        toolbar.addAction("Zoom In")

        toolbar.addAction("Zoom Out")

        toolbar.addAction("Reset View")

    ##################################################

    def create_statusbar(self):

        status = QStatusBar()

        status.showMessage(
            "Atmospheric Complexity Framework Ready"
        )

        self.setStatusBar(status)

    ##################################################

    def refresh(self):
        """
        Refresh the complete interface.
        """

        self.layer_panel.refresh()

        self.dataset_panel.refresh()

        self.map_canvas.refresh()

    ##################################################

    def shutdown(self):
        """
        Close ACF properly.
        """

        self.dashboard.shutdown()
