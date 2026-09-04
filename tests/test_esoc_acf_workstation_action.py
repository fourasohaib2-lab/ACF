"""
Tests for ESOCWindow's "🔬 ACF Scientific Workstation" toolbar action -
opens the real, AWCI-free ACF Scientific Workstation
(acf.gui.dashboard.acf_workstation_window.ACFWorkstationWindow), same
open-or-raise pattern already tested for the "✈️ AWCI"/"🌪️ AWCI Field"
actions (tests/test_esoc_awci_field.py).

NOTE (correction, 2026-09-04): this replaces
tests/test_esoc_acf_general_dashboard_action.py - the toolbar action it
tested ("🌐 ACF Dashboard" -> ACFGeneralDashboardWindow) was repointed
to the real, genuinely AWCI-free ACFWorkstationWindow after a real
audit found ACFGeneralDashboard AWCI-coupled despite its name (see
acf_general_dashboard.py's own NOTE).
"""

from __future__ import annotations

from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow


def test_toolbar_has_the_real_acf_workstation_action(qtbot):
    toolbar = ESOCToolbar()
    qtbot.addWidget(toolbar)
    action_labels = [act.text() for act in toolbar.actions()]
    assert "🔬 ACF Scientific Workstation" in action_labels
    assert "🌐 ACF Dashboard" not in action_labels  # the old, AWCI-coupled entry is gone


def test_open_acf_workstation_creates_and_shows_the_window(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)
    assert win._acf_workstation_window is None

    win._open_acf_workstation()

    assert win._acf_workstation_window is not None
    assert win._acf_workstation_window.isVisible() is True
    # Opening the window is a real user action - refresh() DOES fire here
    # (unlike bare ACFWorkstation() construction) per
    # ACFWorkstationWindow's own __init__.
    qtbot.waitUntil(lambda: win._acf_workstation_window.workstation._volume is not None, timeout=60000)


def test_open_acf_workstation_reuses_the_same_window_on_a_second_call(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)

    win._open_acf_workstation()
    first = win._acf_workstation_window
    win._open_acf_workstation()

    assert win._acf_workstation_window is first


def test_toolbar_action_dispatch_reaches_the_real_handler(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)

    win._handle_toolbar_action("open_acf_workstation")

    assert win._acf_workstation_window is not None
