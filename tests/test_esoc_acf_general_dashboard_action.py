"""
Tests for ESOCWindow's "🌐 ACF Dashboard" toolbar action - opens the
general ACF research dashboard (acf.gui.dashboard.acf_general_dashboard_window.
ACFGeneralDashboardWindow), same open-or-raise pattern already tested for
the "✈️ AWCI"/"🌪️ AWCI Field" actions (tests/test_esoc_awci_field.py).
"""

from __future__ import annotations

from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow


def test_toolbar_has_the_real_acf_general_dashboard_action(qtbot):
    toolbar = ESOCToolbar()
    qtbot.addWidget(toolbar)
    action_labels = [act.text() for act in toolbar.actions()]
    assert "🌐 ACF Dashboard" in action_labels


def test_open_acf_general_dashboard_creates_and_shows_the_window(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)
    assert win._acf_general_dashboard_window is None

    win._open_acf_general_dashboard()

    assert win._acf_general_dashboard_window is not None
    assert win._acf_general_dashboard_window.isVisible() is True
    # Opening the window is a real user action - refresh() DOES fire here
    # (unlike bare ACFGeneralDashboard() construction) per
    # ACFGeneralDashboardWindow's own __init__.
    qtbot.waitUntil(lambda: win._acf_general_dashboard_window.acf_dashboard._evolution is not None, timeout=60000)


def test_open_acf_general_dashboard_reuses_the_same_window_on_a_second_call(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)

    win._open_acf_general_dashboard()
    first = win._acf_general_dashboard_window
    win._open_acf_general_dashboard()

    assert win._acf_general_dashboard_window is first


def test_toolbar_action_dispatch_reaches_the_real_handler(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)

    win._handle_toolbar_action("open_acf_general_dashboard")

    assert win._acf_general_dashboard_window is not None
