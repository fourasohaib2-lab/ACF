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
