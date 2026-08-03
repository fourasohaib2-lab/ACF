"""Atmospheric Complexity Framework (ACF) GUI Application Launcher.

Launches the Unified Earth System Operations Center (ESOC) (ACF-UI-012).
"""

import sys
import time

from PySide6.QtWidgets import QApplication

from acf.gui.esoc.esoc_window import ESOCWindow
from acf.gui.splash import SplashScreen
from acf.gui.theme import ThemeManager


def run() -> None:
    """Official application entry point launching ESOCWindow."""
    app = QApplication(sys.argv)

    theme = ThemeManager()
    app.setStyleSheet(theme.stylesheet())

    splash = SplashScreen()
    splash.show()

    app.processEvents()

    time.sleep(2)

    # Boot into ESOCWindow as default operational command interface
    window = ESOCWindow()
    window.show()

    splash.close()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()
