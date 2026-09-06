"""Atmospheric Complexity Framework (ACF) GUI Application Launcher.

Launches the Unified Earth System Operations Center (ESOC) (ACF-UI-012).
"""

import sys
import time

from PySide6.QtWidgets import QApplication

from acf import __version__
from acf.gui.esoc.esoc_window import ESOCWindow
from acf.gui.main_window.main_window import MainWindow
from acf.gui.single_instance import SingleInstanceGuard
from acf.gui.splash import SplashScreen
from acf.gui.theme import ThemeManager

__all__ = ["ESOCWindow", "MainWindow", "main", "run"]


def run() -> None:
    """Official application entry point launching ESOCWindow."""
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"Atmospheric Complexity Framework (ACF) v{__version__}")
        return
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: acf-gui [OPTIONS]")
        print("\nOptions:")
        print("  -v, --version  Show ACF version and exit.")
        print("  -h, --help     Show this message and exit.")
        return

    from acf.gui.bootstrap import configure_runtime

    configure_runtime()

    app = QApplication(sys.argv)

    # NOTE (correction, 2026-09-06 - real user-reported bug: "plusieurs
    # dashboard qui s'affiche au meme temps" / several dashboards
    # showing at once): nothing here used to check whether an ESOC
    # instance was already running - launching acf-gui again (a second
    # double-click, a re-run, a stray autostart entry) built a brand
    # new, fully independent ESOCWindow every time, with zero
    # coordination between them. SingleInstanceGuard uses a real
    # QLocalServer/QLocalSocket handshake (see its own docstring) - if
    # another real instance answers, this process asks it to raise its
    # window and exits immediately, before building any UI of its own.
    guard = SingleInstanceGuard()
    if not guard.acquire():
        return

    theme = ThemeManager()
    app.setStyleSheet(theme.stylesheet())

    splash = SplashScreen()
    splash.show()

    app.processEvents()

    time.sleep(2)

    # Boot into ESOCWindow as default operational command interface
    window = ESOCWindow()
    window.show()

    def _activate_existing_window() -> None:
        window.showNormal()
        window.raise_()
        window.activateWindow()

    guard.activation_requested.connect(_activate_existing_window)

    splash.close()

    sys.exit(app.exec())


def main() -> None:
    """Official CLI entry point for the ACF GUI."""
    run()


if __name__ == "__main__":
    main()
