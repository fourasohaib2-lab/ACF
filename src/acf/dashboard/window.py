"""
ACF Classic Dashboard Window
=============================

Standalone QMainWindow hosting the "classic" ACF dashboard
(DashboardManager -> Dashboard -> DashboardLayout: central MapView plus
Explorer / Charts / Properties / Timeline / Console / Status docks).

NOTE (context): this dashboard package (acf.dashboard) predates ESOC
(acf.gui.esoc.esoc_window.ESOCWindow, the application's current primary
window - see acf-gui's own entry point) and was completely unreachable
from the running application: nothing outside this package's own test
suite (test_dashboard_manager.py, test_dashboard_gui_construction.py)
ever constructed a Dashboard/DashboardManager against a real window.
DashboardLayout.build() calls window.setCentralWidget()/addDockWidget()
directly, so - unlike the AWCI dashboard, which fit naturally as one more
tab inside ESOC's bottom dock - this one wants to own an entire top-level
window, not be embedded inside another one's panel area. This class gives
it that window and is launched as a separate, non-modal window from ESOC's
toolbar ("Classic View" action) rather than forcing it into a tab.
"""

from typing import Any

from PySide6.QtWidgets import QMainWindow

from acf.dashboard.manager import DashboardManager


class ClassicDashboardWindow(QMainWindow):
    """Standalone window for the classic ACF dashboard."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("ACF Classic Dashboard")
        self.resize(1400, 900)

        self.manager = DashboardManager(self)
        self.manager.initialize()

    def status(self) -> dict[str, Any]:
        return self.manager.status()

    def closeEvent(self, event: Any) -> None:  # noqa: N802 - Qt override signature
        self.manager.shutdown()
        super().closeEvent(event)
