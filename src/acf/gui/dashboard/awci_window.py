"""
AWCI Dashboard Window
======================

Standalone QMainWindow hosting the AWCIDashboard widget, so it can be
opened as its own window from a button inside the main ACF dashboard
(acf.dashboard.window.ClassicDashboardWindow) - matching the requested
relationship: ACF main dashboard is the primary window, AWCI dashboard is
a secondary one opened from it.
"""

from typing import Any

from PySide6.QtWidgets import QMainWindow

from acf.gui_screen_utils import fit_window_to_screen
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


class AWCIDashboardWindow(QMainWindow):
    """Standalone window hosting the AWCI operational dashboard."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AWCI – Aviation Weather Complexity Index")
        # NOTE (correction): was a hardcoded self.resize(1500, 950), which
        # could exceed a smaller screen's available geometry. Clamp to what
        # the screen actually offers instead (see acf.gui_screen_utils).
        fit_window_to_screen(self, 1500, 950)

        self.awci_dashboard = AWCIDashboard()
        self.setCentralWidget(self.awci_dashboard)

    def status(self) -> dict[str, Any]:
        return {"awci_dashboard": self.awci_dashboard is not None}
