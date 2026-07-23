#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo "ACF Sprint 03 - Part 5"
echo "Theme Manager"
echo "========================================="

cd "$PROJECT"

mkdir -p src/acf/gui/resources/themes

###############################################################################
# dark.qss
###############################################################################

cat > src/acf/gui/resources/themes/dark.qss << 'EOF'
QMainWindow {
    background-color: #202124;
}

QMenuBar {
    background-color: #2b2b2b;
    color: white;
}

QMenuBar::item:selected {
    background-color: #1565C0;
}

QMenu {
    background-color: #2b2b2b;
    color: white;
}

QToolBar {
    background-color: #303134;
}

QStatusBar {
    background-color: #303134;
    color: white;
}

QDockWidget {
    color: white;
}

QListWidget,
QTextEdit,
QLabel {
    background-color: #252526;
    color: white;
    border: 1px solid #3c3c3c;
}
EOF

###############################################################################
# light.qss
###############################################################################

cat > src/acf/gui/resources/themes/light.qss << 'EOF'
QMainWindow {
    background: white;
}

QMenuBar {
    background: #eeeeee;
}

QMenuBar::item:selected {
    background: #90CAF9;
}

QToolBar {
    background: #f5f5f5;
}

QStatusBar {
    background: #f5f5f5;
}

QListWidget,
QTextEdit,
QLabel {
    background: white;
    color: black;
    border: 1px solid lightgray;
}
EOF

###############################################################################
# theme.py
###############################################################################

cat > src/acf/gui/theme.py << 'EOF'
from pathlib import Path

class ThemeManager:

    def __init__(self):
        self.theme = "dark"

    def stylesheet(self):

        root = Path(__file__).parent

        file = root / "resources" / "themes" / f"{self.theme}.qss"

        return file.read_text(encoding="utf-8")

    def set_theme(self, name):

        self.theme = name
EOF

###############################################################################
# app.py
###############################################################################

cat > src/acf/gui/app.py << 'EOF'
import sys

from PySide6.QtWidgets import QApplication

from acf.gui.main_window import MainWindow
from acf.gui.theme import ThemeManager


def run():

    app = QApplication(sys.argv)

    theme = ThemeManager()

    app.setStyleSheet(theme.stylesheet())

    window = MainWindow()

    window.show()

    sys.exit(app.exec())
EOF

echo
echo "Theme Manager installed successfully."
