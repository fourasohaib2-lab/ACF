#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo "ACF Sprint 03 - Part 6"
echo "Splash Screen"
echo "========================================="

cd "$PROJECT"

###############################################################################
# splash.py
###############################################################################

cat > src/acf/gui/splash.py << 'EOF'
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ACF Loading")
        self.setFixedSize(600, 300)

        layout = QVBoxLayout(self)

        title = QLabel("Atmospheric Complexity Framework")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px;font-weight:bold;")

        version = QLabel("Version 0.1.0-alpha")
        version.setAlignment(Qt.AlignCenter)

        status = QLabel("Initializing ACF...")
        status.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(status)
        layout.addStretch()
EOF

###############################################################################
# app.py
###############################################################################

cat > src/acf/gui/app.py << 'EOF'
import sys
import time

from PySide6.QtWidgets import QApplication

from acf.gui.main_window import MainWindow
from acf.gui.splash import SplashScreen
from acf.gui.theme import ThemeManager


def run():

    app = QApplication(sys.argv)

    theme = ThemeManager()
    app.setStyleSheet(theme.stylesheet())

    splash = SplashScreen()
    splash.show()

    app.processEvents()

    time.sleep(2)

    window = MainWindow()
    window.show()

    splash.close()

    sys.exit(app.exec())
EOF

echo
echo "Splash Screen installed successfully."
