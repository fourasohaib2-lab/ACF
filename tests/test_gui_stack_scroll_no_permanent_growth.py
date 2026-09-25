"""
Regression test: switching to a large Lab panel must not PERMANENTLY
grow ACFWorkstationWindow.

`CurrentPageStackedWidget`/`CurrentPageTabWidget` (acf.gui.widgets.
current_page_sizing) stop a QStackedWidget/QTabWidget from being
floored at its single largest page - but that alone is not enough: a
real top-level window (QMainWindow included) never auto-shrinks its
actual on-screen size just because its computed minimum size went
down; it only auto-grows when the minimum goes up. Measured before this
fix: opening ACFWorkstation's "Complexity Explorer" Lab panel (737px
tall) even once grew the whole window from 633 to 978px, and it then
STAYED there after switching back to a tiny panel - on a small screen,
a single visit to a heavy panel permanently outgrows the display.

The fix wraps `ACFWorkstation.stack` in its own `QScrollArea`
(`setWidgetResizable(True)`) - the exact same pattern this codebase
already uses for `AWCIDashboardPanel`, for the identical reason (see
that class's own docstring) - which fully decouples the window's own
minimum size from any one panel's content: a panel that doesn't fit
the space actually given scrolls instead of forcing the window to grow.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_window import ACFWorkstationWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_acf_workstation_window_does_not_permanently_grow_after_visiting_complexity_explorer(qapp):
    window = ACFWorkstationWindow()
    window.show()
    workstation = window.workstation

    initial_height = window.height()

    workstation.stack.setCurrentWidget(workstation.complexity_panel)
    qapp.processEvents()
    assert window.height() == initial_height

    workstation.stack.setCurrentWidget(workstation.overview_panel)
    qapp.processEvents()
    assert window.height() == initial_height


def test_acf_workstation_window_can_still_be_explicitly_shrunk_after_visiting_complexity_explorer(qapp):
    """The Workstation window has its own always-visible right-hand column
    (sounding/stability/interaction-graph/forecast-consistency panels)
    with a genuine, legitimate minimum height of its own - so shrinking
    below THAT floor is not expected. What this guards against is the
    other bug: without the scroll wrap, "Complexity Explorer"'s own
    737px minimum used to be permanently baked into the window's floor
    even after leaving that panel - so explicitly resizing smaller than
    737 (but still at/above the window's own legitimate chrome minimum)
    must now succeed."""
    window = ACFWorkstationWindow()
    window.show()
    workstation = window.workstation

    workstation.stack.setCurrentWidget(workstation.complexity_panel)
    qapp.processEvents()
    workstation.stack.setCurrentWidget(workstation.overview_panel)
    qapp.processEvents()

    own_chrome_minimum = window.minimumSizeHint().height()
    assert own_chrome_minimum < 737, "the window's own real minimum must no longer include Complexity Explorer's 737px"

    window.resize(700, own_chrome_minimum + 20)
    qapp.processEvents()
    assert window.height() < 737
