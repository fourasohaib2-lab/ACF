"""
Atmospheric Complexity Framework (ACF)

Main Window
===========

Professional main application window.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
)

from acf.gui.main_window.menu_bar import ACFMenuBar
from acf.gui.main_window.tool_bar import ACFToolBar
from acf.gui.main_window.status_bar import ACFStatusBar
from acf.gui.main_window.property_panel import PropertyPanel

from acf.gui.layer_panel.layer_panel import LayerPanel

from acf.gui.map.map_canvas import MapCanvas


class MainWindow(QMainWindow):
    """
    Professional ACF Main Window.
    """

    ##################################################

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Atmospheric Complexity Framework"
        )

        self.resize(1700, 950)

        ##################################################
        # Widgets
        ##################################################

        self.layer_panel = LayerPanel()

        self.map_canvas = MapCanvas()

        self.property_panel = PropertyPanel()

        ##################################################
        # Central Widget
        ##################################################

        central = QWidget()

        layout = QHBoxLayout()

        layout.setContentsMargins(2, 2, 2, 2)

        layout.setSpacing(2)

        ##################################################

        self.layer_panel.setMinimumWidth(280)

        self.layer_panel.setMaximumWidth(320)

        self.property_panel.setMinimumWidth(260)

        self.property_panel.setMaximumWidth(320)

        ##################################################

        layout.addWidget(self.layer_panel)

        layout.addWidget(self.map_canvas, 1)

        layout.addWidget(self.property_panel)

        ##################################################

        central.setLayout(layout)

        self.setCentralWidget(central)

        ##################################################
        # Menu / Toolbar / Status
        ##################################################

        self.menu = ACFMenuBar(self)

        self.toolbar = ACFToolBar(self)

        self.status = ACFStatusBar(self)

        ##################################################
        # First map
        ##################################################

        self.map_canvas.draw_world()

        ##################################################

        self.status.set_message(
            "ACF initialized successfully."
        )
