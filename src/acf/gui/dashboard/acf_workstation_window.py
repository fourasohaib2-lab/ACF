"""
ACF Scientific Workstation Window
====================================

Standalone QMainWindow hosting the ACFWorkstation widget, so it can be
opened/raised from ESOC's own "ACF Dashboard" toolbar action - same
open-or-raise pattern already used for AWCIDashboardWindow
(acf.gui.dashboard.awci_window) and ACFGeneralDashboardWindow
(acf.gui.dashboard.acf_general_dashboard_window, which this window now
replaces as that toolbar action's real target - see esoc_window.py's
own NOTE).
"""

from typing import Any

from PySide6.QtWidgets import QMainWindow

from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.gui_screen_utils import fit_window_to_screen


class ACFWorkstationWindow(QMainWindow):
    """Standalone window hosting the real ACF Scientific Workstation."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("ACF Scientific Workstation")
        fit_window_to_screen(self, 1600, 1000)

        self.workstation = ACFWorkstation()
        self.setCentralWidget(self.workstation)
        # Auto-populate the real volume once on open - a genuine user
        # action (opening the window), not a bare construction, so this
        # does not fire from a unit test that merely instantiates
        # ACFWorkstation() directly (see that class's own __init__
        # docstring note for why the widget itself stays inert until
        # asked - same convention as ACFGeneralDashboardWindow).
        self.workstation.refresh()

    def status(self) -> dict[str, Any]:
        return {"workstation": self.workstation is not None}
