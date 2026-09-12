"""
Tests for acf.gui.dashboard.awci_sidebar.AWCISidebar - the real light
sidebar navigation shell added 2026-09-12 (docs/reference/
awci_dashboard_reference.png, explicit user request "je veux que le
dashboard soit exactement comme celui dans la photo... 100%... tous
les boutons fonctionnelles").
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_sidebar import NAV_SECTIONS, AWCISidebar


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _all_items():
    for _section_name, items in NAV_SECTIONS:
        yield from items


def test_overview_is_the_default_active_item(qapp):
    sidebar = AWCISidebar()
    assert sidebar._buttons["overview"].isChecked() is True


def test_every_enabled_item_emits_its_real_key_on_click(qapp):
    sidebar = AWCISidebar()
    seen = []
    sidebar.navItemClicked.connect(seen.append)
    for item in _all_items():
        if not item.enabled:
            continue
        sidebar._buttons[item.key].click()
        assert seen[-1] == item.key


def test_disabled_items_are_real_qt_disabled_and_never_emit(qapp):
    """Real, honest gaps (Airport Analysis, Wind Shear, Precipitation,
    Snow & Icing Accumulation, Volcanic Ash, API) are constructed
    genuinely disabled (isEnabled() is False) with a disclosing
    tooltip - never a button that looks clickable but silently does
    nothing."""
    sidebar = AWCISidebar()
    seen = []
    sidebar.navItemClicked.connect(seen.append)
    for item in _all_items():
        if item.enabled:
            continue
        button = sidebar._buttons[item.key]
        assert button.isEnabled() is False
        assert button.toolTip() == item.disabled_reason
        assert item.disabled_reason != ""
        button.click()  # a real Qt no-op on a disabled button
    assert seen == []


def test_clicking_one_item_makes_it_the_only_checked_one(qapp):
    sidebar = AWCISidebar()
    sidebar._buttons["map_3d"].click()
    assert sidebar._buttons["map_3d"].isChecked() is True
    assert sidebar._buttons["overview"].isChecked() is False


def test_set_active_checks_the_real_named_item(qapp):
    sidebar = AWCISidebar()
    sidebar.set_active("data_alerts")
    assert sidebar._buttons["data_alerts"].isChecked() is True


def test_set_active_on_a_disabled_item_is_a_real_no_op(qapp):
    sidebar = AWCISidebar()
    sidebar.set_active("map_airport")
    assert sidebar._buttons["map_airport"].isChecked() is False


def test_nav_item_keys_are_unique(qapp):
    keys = [item.key for item in _all_items()]
    assert len(keys) == len(set(keys))
