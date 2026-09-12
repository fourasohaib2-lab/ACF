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

from acf.gui_screen_utils import compute_screen_scale, fit_window_to_screen
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


class AWCIDashboardWindow(QMainWindow):
    """Standalone window hosting the AWCI operational dashboard."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AWCI – Aviation Weather Complexity Index")

        # Real screen-adaptability fix (2026-09-07, explicit user
        # request "assure toi que la resolution est adaptable selon le
        # type d'ecran elle est ajustable") - see compute_screen_scale's
        # own docstring for the real 1366x768/1280x800/2560x1440
        # measurements behind this. `self.screen()` already resolves to
        # a real screen before the window is shown (Qt6 defaults it to
        # the primary screen), same real resolution mechanism
        # fit_window_to_screen below already relies on.
        self._screen_scale = compute_screen_scale(self)
        self.awci_dashboard = AWCIDashboard(screen_scale=self._screen_scale)
        # NOTE (correction, 2026-09-07 - real bug, found from a real
        # screenshot while modernizing this dashboard's visual design,
        # not a code read): this used to call fit_window_to_screen(self,
        # 1500, 950) BEFORE self.awci_dashboard existed, so the fixed
        # 1500 guess had no way to know the header row's own real
        # natural width. Measured directly: the header (title + 🔬 Real
        # Physics/🧊 3D View/📨 Message/🔔 Alerts/📊 Report/📡 Real
        # Archive buttons + the RESEARCH STAGE badge) needs ~1533px,
        # 33px more than the fixed guess - the badge's own right edge
        # was genuinely clipped, confirmed in a real screenshot, on a
        # screen plenty large enough to fit either width (1920x1080 -
        # this was never actually a screen-size problem, despite an
        # earlier pass in this same session initially misdiagnosing it
        # as one by comparing against the wrong screen). Now sized from
        # the dashboard's own real, current sizeHint() - self-correcting
        # if a future change grows or shrinks the header, instead of a
        # second guessed constant that would just as easily go stale
        # again. Still screen-clamped exactly as before (unchanged for
        # a genuinely small screen, where the QScrollArea below already
        # takes over, per this class's own next NOTE).
        fit_window_to_screen(self, self.awci_dashboard.sizeHint().width(), 950)
        # NOTE (real responsive-sizing fix, 2026-09-05): AWCIDashboard's
        # own real, stacked maps/charts (global map, cross-section,
        # regional map, regional trend, ...) give it a genuine minimum
        # size of ~1489x1064, measured - larger than plenty of real
        # screens (1366x768/1280x800/1024x768 laptops), so the clamp
        # above alone can't keep this window on-screen: Qt floors a
        # QMainWindow's actual minimum to its central widget's, no
        # matter what resize() was asked for. Wrapped in a QScrollArea -
        # the window's own minimum drops to just the scroll area's frame,
        # so the window can
        # always shrink to whatever the operator's screen allows, with
        # scrollbars for whatever doesn't fit instead of the window
        # itself growing past the display.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.awci_dashboard)
        self.setCentralWidget(scroll)

    def status(self) -> dict[str, Any]:
        return {"awci_dashboard": self.awci_dashboard is not None}
