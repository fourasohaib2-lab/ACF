"""Atmospheric Weather Complexity Index (AWCI) — standalone launcher.

Genuinely independent from acf.gui.app (ESOC): its own QApplication, its
own process when launched via `acf-awci` / `python -m acf.awci_app` /
ESOC's own "Launch AWCI App" toolbar action (which spawns this as a real
subprocess, not an in-process second window - see esoc_window.py's
_launch_awci_app()). Closing ESOC does not close this, and closing this
does not close ESOC: two separate OS processes, each with their own
single-instance guard (different server name - see SingleInstanceGuard's
own docstring for what that guards against), not a shared one.

This does not replace ESOC's existing in-process "✈️ AWCI" toolbar
button (esoc_window.py's own _open_awci_dashboard(), which opens
AWCIDashboardWindow as a second window in ESOC's own process, useful
when a lighter-weight embedded view is enough) - it is a genuinely
different, additional way to reach the same real AWCIDashboardWindow,
for when an operator wants AWCI to keep running as its own application
independent of ESOC's own lifecycle.
"""

import sys

from PySide6.QtWidgets import QApplication

from acf import __version__
from acf.gui.dashboard.awci_window import AWCIDashboardWindow
from acf.gui.single_instance import SingleInstanceGuard
from acf.gui.theme import ThemeManager

__all__ = ["AWCIDashboardWindow", "main", "run"]

#: Distinct from acf.gui.single_instance's own default SERVER_NAME
#: (ESOC's) - a real second instance of THIS app must still be caught
#: and raise the existing one, but must never collide with, or be
#: confused for, a second ESOC instance.
_AWCI_APP_SERVER_NAME = "acf-awci-app-single-instance"


def run() -> None:
    """Real entry point launching AWCIDashboardWindow as its own application."""
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"ACF AWCI (Atmospheric Weather Complexity Index) v{__version__}")
        return
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: acf-awci [OPTIONS]")
        print("\nOptions:")
        print("  -v, --version  Show AWCI app version and exit.")
        print("  -h, --help     Show this message and exit.")
        return

    from acf.gui.bootstrap import configure_runtime

    configure_runtime()

    app = QApplication(sys.argv)

    guard = SingleInstanceGuard(server_name=_AWCI_APP_SERVER_NAME)
    if not guard.acquire():
        return

    theme = ThemeManager()
    app.setStyleSheet(theme.stylesheet())

    window = AWCIDashboardWindow()
    # NOTE (correction, 2026-09-07 - explicit user request "gère moi la
    # résolution pour que ça soit en plein écran"): was window.show(),
    # opening at fit_window_to_screen's own fixed size. showMaximized()
    # fills the real available screen (keeping the OS window chrome/
    # controls, matching how "plein écran" already reads for every
    # other real desktop window in this project - not a borderless
    # kiosk mode).
    window.showMaximized()

    def _activate_existing_window() -> None:
        # Only un-minimize (real fix, same turn): showNormal()
        # unconditionally would silently un-maximize a real second-
        # instance activation even when the window was never
        # minimized in the first place - restoring it to
        # fit_window_to_screen's smaller fixed size instead of leaving
        # it maximized.
        if window.isMinimized():
            window.showNormal()
        window.raise_()
        window.activateWindow()

    guard.activation_requested.connect(_activate_existing_window)

    sys.exit(app.exec())


def main() -> None:
    """CLI entry point for the standalone AWCI app (console script: acf-awci)."""
    run()


if __name__ == "__main__":
    main()
