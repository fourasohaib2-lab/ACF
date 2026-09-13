"""
Tests for AWCIDashboard's real "☰" header menu (added 2026-09-12,
explicit user request "je veux que le dashboard soit exactement comme
celui dans la photo... ajoute un bouton de trois barres en haut à
droite qui affiche une liste de ses paramètres qui ne figure pas dans
la photo, adapte toi" - docs/reference/awci_dashboard_reference.jpg's
own header shows no buttons at all).

See AWCIDashboard._build_header_menu()'s own docstring for the design:
the 10 real header buttons (+ the UTC clock) are hidden from the
visible header but stay real, connected, and state-synced exactly as
before - this menu is a thin, always-current presentation layer over
that SAME single source of truth, never a second independently-tracked
copy. compare_fl_button (2026-09-13 refonte) joined the original 9 once
its own floating button - the FL280/FL320 comparison, with no place in
the reference photo - was relocated here instead of retired.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


_HIDDEN_BUTTON_ATTRS = (
    "real_physics_button",
    "play_evolution_button",
    "view_3d_button",
    "hpc_button",
    "import_model_button",
    "compare_fl_button",
    "messages_button",
    "alerts_button",
    "execution_report_button",
    "real_archive_button",
)


def test_all_10_real_buttons_and_the_clock_are_hidden_from_the_visible_header(qapp):
    dashboard = AWCIDashboard()
    dashboard.show()
    for attr in _HIDDEN_BUTTON_ATTRS:
        button = getattr(dashboard, attr)
        assert button.isVisible() is False, f"{attr} must not be shown directly in the header any more"
        assert button.parent() is dashboard  # still real, owned widgets - just not in any layout
    assert dashboard.clock_label.isVisible() is False


def test_hamburger_button_exists_with_the_real_menu_attached(qapp):
    dashboard = AWCIDashboard()
    entries = dict(dashboard._header_menu_entries)
    assert len(dashboard._header_menu_entries) == 10
    for attr in _HIDDEN_BUTTON_ATTRS:
        assert getattr(dashboard, attr) in entries


def test_sync_header_menu_mirrors_the_real_button_state(qapp):
    dashboard = AWCIDashboard()
    dashboard.real_physics_button.setText("↩ Back to Demo")
    dashboard.alerts_button.setText("🔔 Alerts (3)")
    dashboard.play_evolution_button.setEnabled(True)

    dashboard._sync_header_menu()

    by_button = dict(dashboard._header_menu_entries)
    assert by_button[dashboard.real_physics_button].text() == "↩ Back to Demo"
    assert by_button[dashboard.alerts_button].text() == "🔔 Alerts (3)"
    assert by_button[dashboard.play_evolution_button].isEnabled() is True


def test_sync_header_menu_refreshes_the_real_live_clock(qapp):
    dashboard = AWCIDashboard()
    dashboard._update_clock()
    expected = dashboard.clock_label.text()

    dashboard._sync_header_menu()

    assert dashboard._header_clock_action.text() == expected
    assert dashboard._header_clock_action.isEnabled() is False


def test_triggering_a_menu_action_calls_the_real_underlying_slot(qapp, monkeypatch):
    """action.triggered is wired to button.click() (not a second,
    duplicated call to the slot) - proven here by watching the REAL
    slot the button itself is connected to actually run."""
    dashboard = AWCIDashboard()
    calls = []
    monkeypatch.setattr(dashboard, "_open_alerts", lambda: calls.append("opened"))
    # Reconnect with the patched slot the same way _build_ui() did with the original.
    dashboard.alerts_button.clicked.disconnect()
    dashboard.alerts_button.clicked.connect(dashboard._open_alerts)

    action = dict(dashboard._header_menu_entries)[dashboard.alerts_button]
    action.trigger()

    assert calls == ["opened"]


def test_triggering_a_disabled_entry_is_a_real_no_op(qapp):
    """view_3d_button starts disabled (no Real Physics volume yet) -
    QPushButton.click() on a disabled button is a real Qt no-op, so the
    menu action must stay just as inert, with no separate enable rule
    duplicated here - real proof: the real 3D view window this click
    would otherwise open stays unopened."""
    dashboard = AWCIDashboard()
    assert dashboard.view_3d_button.isEnabled() is False
    assert dashboard._volume_3d_window is None

    action = dict(dashboard._header_menu_entries)[dashboard.view_3d_button]
    action.trigger()

    assert dashboard._volume_3d_window is None
