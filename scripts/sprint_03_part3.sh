#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo "ACF Sprint 03 - Part 3"
echo "Workspace Layout"
echo "========================================="

cd "$PROJECT"

cat > src/acf/gui/main_window.py << 'EOPY'
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QTextEdit,
    QDockWidget,
    QMainWindow,
    QStatusBar,
    QToolBar,
)

from PySide6.QtGui import QAction


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Atmospheric Complexity Framework"
        )

        self.resize(1600,900)

        self.create_menu()

        self.create_toolbar()

        self.create_statusbar()

        self.create_workspace()

    ###################################################

    def create_menu(self):

        menu=self.menuBar()

        file_menu=menu.addMenu("File")
        edit_menu=menu.addMenu("Edit")
        view_menu=menu.addMenu("View")
        data_menu=menu.addMenu("Data")
        tools_menu=menu.addMenu("Tools")
        plugins_menu=menu.addMenu("Plugins")
        help_menu=menu.addMenu("Help")

        exit_action=QAction("Exit",self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

    ###################################################

    def create_toolbar(self):

        toolbar=QToolBar()

        self.addToolBar(toolbar)

        toolbar.addAction("Open")

        toolbar.addAction("Save")

        toolbar.addAction("Run")

        toolbar.addAction("Stop")

    ###################################################

    def create_statusbar(self):

        status=QStatusBar()

        status.showMessage("Ready")

        self.setStatusBar(status)

    ###################################################

    def create_workspace(self):

        central=QLabel(
            "Scientific Workspace"
        )

        central.setAlignment(Qt.AlignCenter)

        central.setStyleSheet(
            "font-size:24px;"
        )

        self.setCentralWidget(central)

        ##########################################

        explorer=QDockWidget("Project Explorer")

        explorer.setWidget(QListWidget())

        explorer.widget().addItems([
            "Project",
            "Workspace",
            "Datasets",
            "Maps",
            "Models",
            "Plugins",
            "Reports"
        ])

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            explorer
        )

        ##########################################

        properties=QDockWidget(
            "Properties"
        )

        properties.setWidget(QTextEdit())

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            properties
        )

        ##########################################

        console=QDockWidget(
            "Console"
        )

        console.setWidget(QTextEdit())

        self.addDockWidget(
            Qt.BottomDockWidgetArea,
            console
        )

EOPY

echo ""
echo "Workspace created successfully."
