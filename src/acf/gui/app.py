"""
Atmospheric Complexity Framework (ACF)

GUI - App

Purpose:
--------
PySide6 Qt GUI components, dock panels, map canvas controllers, and navigation.

Responsibilities:
-----------------
• Manage app logic and state representations.
• Integrate with the gui subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.gui module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

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
