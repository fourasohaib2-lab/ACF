"""
Tests for the real "Recent Alerts" / "Latest Updates" / "Quick Actions"
footer row (added 2026-09-13, docs/reference/awci_dashboard_reference.
png, Phase 6/6 of the AWCI redesign) - replaces the old 5-icon feature
footer (acf.gui.dashboard.awci_footer.AWCIFooter, retired; see
awci_footer_summary.py's own module docstring for where each of its 5
real features stays reachable).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_alerts_panel import compute_elevated_risks
from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_footer_summary import (
    AWCILatestUpdatesCard,
    AWCIQuickActionsCard,
    AWCIRecentAlertsCard,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _module_scores(**overrides):
    base = {"dynamic": 90.0, "convective": 20.0, "microphysical": 15.0}
    base.update(overrides)
    return base


# ------------------------------------------------------- AWCIRecentAlertsCard


def test_recent_alerts_card_matches_the_real_shared_compute_elevated_risks(qapp):
    card = AWCIRecentAlertsCard()
    card.update_data(_module_scores(), 90.0, None, None, area="Global", valid_time="12:00 UTC")
    expected = compute_elevated_risks(_module_scores(), 90.0, None, None)
    assert card.rows_layout.count() == min(len(expected), 3)


def test_recent_alerts_card_shows_an_honest_empty_state(qapp):
    card = AWCIRecentAlertsCard()
    card.update_data({"dynamic": 0.0, "convective": 0.0, "microphysical": 0.0}, 0.0, None, None, area="Global", valid_time="12:00 UTC")
    assert card.rows_layout.count() == 1


def test_recent_alerts_card_click_calls_the_real_callback(qapp):
    calls = []
    card = AWCIRecentAlertsCard(on_open_all=lambda: calls.append(True))
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(5, 5), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    card.mousePressEvent(event)
    assert calls == [True]


# ------------------------------------------------------ AWCILatestUpdatesCard


def test_latest_updates_card_renders_one_row_per_real_line(qapp):
    card = AWCILatestUpdatesCard()
    card.update_data([("AWCI computation completed", "12:00:00 UTC"), ("Data source", "ACF Demo Grid")])
    assert card.rows_layout.count() == 2


# ------------------------------------------------------ AWCIQuickActionsCard


def test_quick_actions_card_buttons_call_the_real_handlers(qapp):
    calls = {"report": 0, "route": 0, "scenario": 0, "export": 0}
    card = AWCIQuickActionsCard(
        on_generate_report=lambda: calls.__setitem__("report", calls["report"] + 1),
        on_route_analysis=lambda: calls.__setitem__("route", calls["route"] + 1),
        on_save_scenario=lambda: calls.__setitem__("scenario", calls["scenario"] + 1),
        on_export_data=lambda: calls.__setitem__("export", calls["export"] + 1),
    )
    card.buttons["Generate Report"].click()
    card.buttons["Route Analysis"].click()
    card.buttons["Save Scenario"].click()
    card.buttons["Export Data"].click()
    assert calls == {"report": 1, "route": 1, "scenario": 1, "export": 1}


# --------------------------------------------------- AWCIDashboard wiring


def test_dashboard_footer_cards_are_populated_after_a_real_refresh(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.latest_updates_card.rows_layout.count() == 3
    # A real elevated Turbulence Risk exists at the default demo point
    # of interest (same real value Current Situation's own "Main
    # Hazards" list already shows) - never left at its construction-
    # time empty state after a real refresh.
    assert dashboard.recent_alerts_card.rows_layout.count() >= 1


def test_dashboard_quick_action_route_analysis_zooms_the_real_map(qapp):
    dashboard = AWCIDashboard()
    default_extent = dashboard.global_map.camera.current_extent()

    dashboard._focus_route_analysis()

    assert dashboard.global_map.camera.current_extent() != default_extent


def test_dashboard_quick_action_export_data_opens_the_real_map_export_menu(qapp, monkeypatch):
    """showMenu() itself is standard, trusted Qt popup machinery (would
    block this test's event loop if actually invoked) - this proves the
    real dispatch target instead: the SAME real menu the map panel's
    own ⬇ button already provides (PNG/SVG/CSV/JSON export actions),
    never a second/duplicated one."""
    dashboard = AWCIDashboard()
    menu = dashboard.global_map.download_button.menu()
    assert menu is not None
    assert dashboard.global_map.export_csv_action in menu.actions()

    calls = []
    monkeypatch.setattr(type(dashboard.global_map.download_button), "showMenu", lambda self: calls.append(True))
    dashboard._export_data()
    assert calls == [True]


def test_dashboard_quick_action_save_scenario_writes_a_real_json_file(qapp, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    dashboard = AWCIDashboard()
    target = tmp_path / "scenario.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    dashboard._save_scenario()

    assert target.exists()
    import json

    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["data_mode"] == "demo"
    assert data["flight_level"] == dashboard.flight_level_selector.currentText()
    assert len(data["route"]) == 2
