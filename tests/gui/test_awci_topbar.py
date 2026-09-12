"""
Tests for acf.gui.dashboard.awci_topbar.AWCITopBar - the real light
top bar added 2026-09-12 (docs/reference/awci_dashboard_reference.png,
explicit user request "je veux que le dashboard soit exactement comme
celui dans la photo... 100%... tous les boutons fonctionnelles").
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_topbar import AWCITopBar


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_area_combo_has_the_2_real_options(qapp):
    topbar = AWCITopBar()
    items = [topbar.area_combo.itemText(i) for i in range(topbar.area_combo.count())]
    assert items == ["Global", "North Africa"]


def test_area_changed_emits_the_real_selected_text(qapp):
    topbar = AWCITopBar()
    seen = []
    topbar.areaChanged.connect(seen.append)
    topbar.area_combo.setCurrentText("North Africa")
    assert seen == ["North Africa"]


def test_set_status_updates_the_real_label_and_dot_color(qapp):
    topbar = AWCITopBar()
    topbar.set_status(is_real=True, label="REAL PHYSICS")
    assert topbar.status_label.text() == "REAL PHYSICS"
    assert "#22c55e" in topbar.status_dot.styleSheet()

    topbar.set_status(is_real=False, label="DEMO MODE")
    assert topbar.status_label.text() == "DEMO MODE"
    assert "#f59e0b" in topbar.status_dot.styleSheet()


def test_user_button_is_a_real_honest_disabled_placeholder(qapp):
    """No real user-account system exists in ACF yet - see module
    docstring - so this must be genuinely disabled, not a fabricated
    working control."""
    topbar = AWCITopBar()
    assert topbar.user_button.isEnabled() is False
    assert topbar.user_button.toolTip() != ""


def test_real_control_buttons_are_all_enabled(qapp):
    topbar = AWCITopBar()
    for button in (topbar.bell_button, topbar.hpc_button, topbar.settings_button, topbar.now_button):
        assert button.isEnabled() is True
