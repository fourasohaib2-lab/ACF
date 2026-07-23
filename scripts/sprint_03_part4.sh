#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo "ACF Sprint 03 - Part 4"
echo "Professional Widgets"
echo "========================================="

cd "$PROJECT"

###############################################################################
# Explorer Widget
###############################################################################

cat > src/acf/gui/widgets/explorer.py << 'EOPY'
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
EOPY

###############################################################################
# Console Widget
###############################################################################

cat > src/acf/gui/widgets/console.py << 'EOPY'
from PySide6.QtWidgets import QTextEdit

class ConsoleWidget(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.append("ACF Console Ready")
EOPY

###############################################################################
# Property Panel
###############################################################################

cat > src/acf/gui/widgets/property_panel.py << 'EOPY'
from PySide6.QtWidgets import QTextEdit

class PropertyPanel(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setPlainText("Properties")
EOPY

###############################################################################
# Map View
###############################################################################

cat > src/acf/gui/widgets/map_view.py << 'EOPY'
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

class MapView(QLabel):

    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText("Map View (Coming Soon)")
        self.setStyleSheet("""
            font-size:24px;
            border:1px solid gray;
        """)
EOPY

###############################################################################
# Main Window
###############################################################################

cat > src/acf/gui/main_window.py << 'EOPY'
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QMainWindow,
    QStatusBar,
    QToolBar,
)

from acf.gui.widgets.console import ConsoleWidget
from acf.gui.widgets.explorer import ExplorerWidget
from acf.gui.widgets.map_view import MapView
from acf.gui.widgets.property_panel import PropertyPanel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Atmospheric Complexity Framework")
        self.resize(1600, 900)

        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_layout()

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

    def _create_layout(self):
        self.setCentralWidget(MapView())

        explorer = QDockWidget("Project Explorer")
        explorer.setWidget(ExplorerWidget())
        self.addDockWidget(Qt.LeftDockWidgetArea, explorer)

        properties = QDockWidget("Properties")
        properties.setWidget(PropertyPanel())
        self.addDockWidget(Qt.RightDockWidgetArea, properties)

        console = QDockWidget("Console")
        console.setWidget(ConsoleWidget())
        self.addDockWidget(Qt.BottomDockWidgetArea, console)
EOPY

echo
echo "Sprint 03 - Part 4 completed successfully."
