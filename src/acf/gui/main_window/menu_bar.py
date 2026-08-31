"""
Atmospheric Complexity Framework (ACF)

Professional Menu Bar
"""

from PySide6.QtGui import QAction


class ACFMenuBar:
    """
    Professional application menu bar.
    """

    def __init__(self, window):

        self.window = window

        self.menu_bar = window.menuBar()

        self.build()

    ##################################################

    def build(self):

        ##################################################
        # File
        ##################################################

        file_menu = self.menu_bar.addMenu("File")

        file_menu.addAction(QAction("New Project", self.window))
        file_menu.addAction(QAction("Open", self.window))
        file_menu.addAction(QAction("Save", self.window))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self.window))

        ##################################################
        # Edit
        ##################################################

        edit_menu = self.menu_bar.addMenu("Edit")

        edit_menu.addAction(QAction("Undo", self.window))
        edit_menu.addAction(QAction("Redo", self.window))

        ##################################################
        # View
        ##################################################

        view_menu = self.menu_bar.addMenu("View")

        view_menu.addAction(QAction("Layers", self.window))
        view_menu.addAction(QAction("Properties", self.window))

        ##################################################
        # Tools
        ##################################################

        tools_menu = self.menu_bar.addMenu("Tools")

        tools_menu.addAction(QAction("Map Tools", self.window))
        tools_menu.addAction(QAction("Measurements", self.window))

        ##################################################
        # AI
        ##################################################

        ai_menu = self.menu_bar.addMenu("AI")

        ai_menu.addAction(QAction("Forecast Assistant", self.window))
        ai_menu.addAction(QAction("AWCI Analysis", self.window))

        ##################################################
        # Help
        ##################################################

        help_menu = self.menu_bar.addMenu("Help")

        help_menu.addAction(QAction("Documentation", self.window))
        help_menu.addAction(QAction("About ACF", self.window))
