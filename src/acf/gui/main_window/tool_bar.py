"""
Atmospheric Complexity Framework (ACF)

Professional Tool Bar

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): never
constructed anywhere (confirmed by grep across src/) - not even by this
package's own MainWindow. Same situation as this package's own
menu_bar.py: every QAction here (New/Open/Save, Pan/Zoom +/Zoom -/World,
Add Layer/Remove, AI) has zero .triggered.connect() anywhere in this
class, unlike ESOCToolbar (this session's earlier fix - see
esoc_window.py's _handle_toolbar_action), whose equivalent buttons are
now all genuinely wired. An earlier, superseded draft, not something
worth connecting up as-is. Not deleted per project convention.
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

        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

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
