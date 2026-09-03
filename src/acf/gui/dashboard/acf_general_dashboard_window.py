"""
ACF General Dashboard Window
==============================

Standalone QMainWindow hosting the ACFGeneralDashboard widget, so it can
be opened/raised from ESOC's "🌐 ACF Dashboard" toolbar action - same
open-or-raise pattern already used for AWCIDashboardWindow
(acf.gui.dashboard.awci_window).
"""

from typing import Any

from PySide6.QtWidgets import QMainWindow

from acf.gui.dashboard.acf_general_dashboard import ACFGeneralDashboard
from acf.gui_screen_utils import fit_window_to_screen


class ACFGeneralDashboardWindow(QMainWindow):
    """Standalone window hosting the general ACF research dashboard."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("ACF – Atmospheric Complexity Framework Research Suite")
        fit_window_to_screen(self, 1600, 1000)

        self.acf_dashboard = ACFGeneralDashboard()
        self.setCentralWidget(self.acf_dashboard)
        # Auto-populate the real evolution once on open - a genuine user
        # action (opening the window), not a bare construction, so this
        # does not fire from a unit test that merely instantiates
        # ACFGeneralDashboard() directly (see that class's own __init__
        # docstring note for why the widget itself stays inert until
        # asked).
        self.acf_dashboard.refresh()

    def status(self) -> dict[str, Any]:
        return {"acf_dashboard": self.acf_dashboard is not None}
