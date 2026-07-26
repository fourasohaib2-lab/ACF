"""
Atmospheric Complexity Framework (ACF)

Professional Tool Bar
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


class ACFToolBar:
    """
    Professional toolbar.
    """

    def __init__(self, window):

        self.window = window

        self.toolbar = window.addToolBar("Main")

        self.toolbar.setMovable(False)

        self.toolbar.setFloatable(False)

        self.toolbar.setToolButtonStyle(
            Qt.ToolButtonTextUnderIcon
        )

        self.build()

    ##################################################

    def build(self):

        ##################################################
        # Project
        ##################################################

        new_action = QAction("New", self.window)

        open_action = QAction("Open", self.window)

        save_action = QAction("Save", self.window)

        ##################################################

        self.toolbar.addAction(new_action)

        self.toolbar.addAction(open_action)

        self.toolbar.addAction(save_action)

        self.toolbar.addSeparator()

        ##################################################
        # Navigation
        ##################################################

        pan_action = QAction("Pan", self.window)

        zoom_in_action = QAction("Zoom +", self.window)

        zoom_out_action = QAction("Zoom -", self.window)

        world_action = QAction("World", self.window)

        ##################################################

        self.toolbar.addAction(pan_action)

        self.toolbar.addAction(zoom_in_action)

        self.toolbar.addAction(zoom_out_action)

        self.toolbar.addAction(world_action)

        self.toolbar.addSeparator()

        ##################################################
        # Layers
        ##################################################

        add_layer_action = QAction("Add Layer", self.window)

        remove_layer_action = QAction("Remove", self.window)

        ##################################################

        self.toolbar.addAction(add_layer_action)

        self.toolbar.addAction(remove_layer_action)

        self.toolbar.addSeparator()

        ##################################################
        # AI
        ##################################################

        ai_action = QAction("AI", self.window)

        self.toolbar.addAction(ai_action)
