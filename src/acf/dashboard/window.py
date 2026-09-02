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
directly, so - unlike the AWCI dashboard, which also fits as an ESOC
tab - this one wants to own an entire top-level window, not be embedded
inside another one's panel area. This class gives it that window and is
launched as a separate, non-modal window from ESOC's toolbar ("Classic
View" action).

This is the main ACF dashboard: it carries its own "✈️ AWCI Dashboard"
button opening the AWCI dashboard as a secondary window from here, per
the requested relationship (ACF dashboard is primary, AWCI is opened
from a button inside it) - not just two independent windows both hanging
off ESOC.
"""

from typing import TYPE_CHECKING, Any

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QToolBar

from acf.dashboard.manager import DashboardManager

if TYPE_CHECKING:
    from acf.gui.dashboard.awci_window import AWCIDashboardWindow


class ClassicDashboardWindow(QMainWindow):
    """Standalone window for the classic ACF dashboard."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("ACF Classic Dashboard")
        self.resize(1400, 900)

        self.manager = DashboardManager(self)
        self.manager.initialize()

        self._awci_window: AWCIDashboardWindow | None = None
        self._build_toolbar()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("ACF Dashboard Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        awci_action = QAction("✈️ AWCI Dashboard", self)
        awci_action.triggered.connect(self.open_awci_dashboard)
        toolbar.addAction(awci_action)

    def open_awci_dashboard(self) -> None:
        """Open (or raise) the AWCI dashboard as a secondary window.

        NOTE: the import is deliberately local, not at module level -
        acf.gui.dashboard.awci_window pulls in acf.gui.dashboard, and
        importing acf.gui at all triggers acf/gui/__init__.py, which
        eagerly imports ESOCWindow, which itself imports
        ClassicDashboardWindow (this class) for its 'Classic View' toolbar
        action - a module-level import here would be a circular import
        (confirmed: raises ImportError on a partially-initialized module).
        Deferring it until the button is actually clicked breaks the cycle,
        since by then every module involved has finished loading.
        """
        from acf.gui.dashboard.awci_window import AWCIDashboardWindow

        if self._awci_window is None:
            self._awci_window = AWCIDashboardWindow(self)
        self._awci_window.show()
        self._awci_window.raise_()
        self._awci_window.activateWindow()

    def status(self) -> dict[str, Any]:
        return self.manager.status()

    def closeEvent(self, event: Any) -> None:  # noqa: N802 - Qt override signature
        self.manager.shutdown()
        super().closeEvent(event)
