"""
ACF General Dashboard Window
==============================

NOTE (correction, 2026-09-04): no longer ESOC's "ACF Dashboard"
toolbar target - see acf_general_dashboard.py's own NOTE (the
dashboard it hosts turned out to be AWCI-coupled despite its name;
acf_workstation_window.ACFWorkstationWindow is the real, genuinely
AWCI-free replacement now wired there). Kept, not deleted, per project
convention - real, tested, working code.

Standalone QMainWindow hosting the ACFGeneralDashboard widget - same
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
