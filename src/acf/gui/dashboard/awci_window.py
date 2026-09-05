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

from PySide6.QtWidgets import QMainWindow, QScrollArea

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
        # NOTE (real responsive-sizing fix, 2026-09-05): AWCIDashboard's
        # own real, stacked maps/charts (global map, cross-section,
        # regional map, regional trend, ...) give it a genuine minimum
        # size of ~1489x1064, measured - larger than plenty of real
        # screens (1366x768/1280x800/1024x768 laptops), so the clamp
        # above alone can't keep this window on-screen: Qt floors a
        # QMainWindow's actual minimum to its central widget's, no
        # matter what resize() was asked for. Wrapped in a QScrollArea -
        # the exact same pattern, and the exact same real widget class,
        # `PanelManager.AWCIDashboardPanel` already uses to embed this
        # identical dashboard inside ESOC's own dock for the identical
        # reason (see that class's own docstring) - so the window can
        # always shrink to whatever the operator's screen allows, with
        # scrollbars for whatever doesn't fit instead of the window
        # itself growing past the display.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.awci_dashboard)
        self.setCentralWidget(scroll)

    def status(self) -> dict[str, Any]:
        return {"awci_dashboard": self.awci_dashboard is not None}
