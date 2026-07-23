#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

cat > "$PROJECT/src/acf/gui/main_window.py" << 'EOF'
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QToolBar,
    QStatusBar,
)

from acf.dashboard.manager import DashboardManager
from acf.workspace.manager import WorkspaceManager


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.workspace = WorkspaceManager()

        self.setWindowTitle("Atmospheric Complexity Framework")
        self.resize(1600, 900)

        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()

        self.dashboard = DashboardManager(self)
        self.dashboard.initialize()

    def _create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        menu.addMenu("Edit")
        menu.addMenu("View")
        menu.addMenu("Data")
        menu.addMenu("Tools")
        menu.addMenu("Plugins")
        menu.addMenu("Help")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction("Open")
        toolbar.addAction("Save")
        toolbar.addAction("Run")
        toolbar.addAction("Stop")

    def _create_statusbar(self):
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)
EOF

echo "MainWindow repaired successfully."
