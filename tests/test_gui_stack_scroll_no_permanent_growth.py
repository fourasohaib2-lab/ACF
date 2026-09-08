"""
Regression test: switching to a large Lab/tab panel must not
PERMANENTLY grow ESOCWindow/ACFWorkstationWindow.

`CurrentPageStackedWidget`/`CurrentPageTabWidget` (acf.gui.widgets.
current_page_sizing) stop a QStackedWidget/QTabWidget from being
floored at its single largest page - but that alone is not enough: a
real top-level window (QMainWindow included) never auto-shrinks its
actual on-screen size just because its computed minimum size went
down; it only auto-grows when the minimum goes up. Measured before this
fix: opening ESOCWindow's "Products" tab (620px tall) even once grew
the whole window from 736 to 1051px, and it then STAYED there after
switching back to a tiny tab - on a small screen, a single visit to a
heavy tab/panel permanently outgrows the display. Same measured effect
for ACFWorkstation's "Complexity Explorer" Lab panel (737px tall, 633
-> 978).

The fix wraps `ESOCLayout.bottom_tabs`/`ACFWorkstation.stack` each in
their own `QScrollArea` (`setWidgetResizable(True)`) - the exact same
pattern this codebase already uses for `AWCIDashboardPanel` inside
`PanelManager`, for the identical reason (see that class's own
docstring) - which fully decouples the window's own minimum size from
any one page/tab's content: a page that doesn't fit the space actually
given scrolls instead of forcing the window to grow.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_window import ACFWorkstationWindow
from acf.gui.esoc.esoc_window import ESOCWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_esoc_window_does_not_permanently_grow_after_visiting_a_large_tab(qapp):
    window = ESOCWindow()
    window.show()
    layout_manager = window.layout_manager

    initial_height = window.height()

    products_panel = layout_manager.panel_manager.get_panel("products")
    assert products_panel is not None, "the 'products' panel this test targets must exist"
    products_index = layout_manager.bottom_tabs.indexOf(products_panel)
    assert products_index != -1

    layout_manager.bottom_tabs.setCurrentIndex(products_index)
    qapp.processEvents()
    # A large tab is allowed to be scrolled internally, but must not
    # force the whole window taller.
    assert window.height() == initial_height

    hpc_panel = layout_manager.panel_manager.get_panel("hpc_dashboard")
    assert hpc_panel is not None
    hpc_index = layout_manager.bottom_tabs.indexOf(hpc_panel)
    layout_manager.bottom_tabs.setCurrentIndex(hpc_index)
    qapp.processEvents()
    assert window.height() == initial_height


def test_esoc_window_can_still_be_explicitly_shrunk_after_visiting_a_large_tab(qapp):
    window = ESOCWindow()
    window.show()
    layout_manager = window.layout_manager

    products_panel = layout_manager.panel_manager.get_panel("products")
    layout_manager.bottom_tabs.setCurrentIndex(layout_manager.bottom_tabs.indexOf(products_panel))
    qapp.processEvents()

    window.resize(700, 500)
    qapp.processEvents()
    assert window.height() == 500


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
    """Unlike ESOCWindow (whose only other dock content is small), the
    Workstation window has its own always-visible right-hand column
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
