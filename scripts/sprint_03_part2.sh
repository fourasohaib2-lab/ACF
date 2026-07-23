#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo "ACF Sprint 03 - Part 2"
echo "Main Window"
echo "========================================="

cd "$PROJECT"

###########################################################
# app.py
###########################################################

cat > src/acf/gui/app.py << 'EOPY'
import sys

from PySide6.QtWidgets import QApplication

from acf.gui.main_window import MainWindow


def run():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
EOPY

###########################################################
# main_window.py
###########################################################

cat > src/acf/gui/main_window.py << 'EOPY'
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
)

from PySide6.QtGui import QAction


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Atmospheric Complexity Framework (ACF)")
        self.resize(1400,900)

        self.create_menu()

        self.create_toolbar()

        self.create_statusbar()

        label = QLabel(
            "Welcome to Atmospheric Complexity Framework"
        )

        label.setStyleSheet(
            "font-size:20px;padding:30px;"
        )

        self.setCentralWidget(label)

    def create_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        view_menu = menu.addMenu("View")
        tools_menu = menu.addMenu("Tools")
        plugins_menu = menu.addMenu("Plugins")
        help_menu = menu.addMenu("Help")

        exit_action = QAction("Exit", self)

        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

    def create_toolbar(self):

        toolbar = QToolBar("Main Toolbar")

        self.addToolBar(toolbar)

        toolbar.addAction("Open")

        toolbar.addAction("Save")

        toolbar.addAction("Run")

    def create_statusbar(self):

        status = QStatusBar()

        status.showMessage("Ready")

        self.setStatusBar(status)
EOPY

###########################################################
# main.py
###########################################################

cat > src/acf/main.py << 'EOPY'
from acf.gui.app import run

if __name__ == "__main__":
    run()
EOPY

echo ""
echo "Desktop Framework created."
