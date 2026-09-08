"""
Tests for acf.gui.esoc.panel_manager.PluginsPanel - the real Plugin
Directory browser closing the previously-empty "Plugins" System
Explorer category (2026-09-04, second of 7 ESOC categories with no
real panel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.core.plugin_manager import PluginManager
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import PluginsPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_plugins_panel_shows_the_real_scanned_plugin_directory(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = PluginsPanel(registry, dispatcher)

    assert "Real, live scan of:" in panel.dir_label.text()
    manager = registry.get_module("plugins")
    assert str(manager.plugin_dir.resolve()) in panel.dir_label.text()


def test_plugins_panel_table_matches_the_real_manager_directly(qapp):
    """Cross-check discipline: the real table must equal an
    independent, direct call to the real PluginManager.list_plugins()."""
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = PluginsPanel(registry, dispatcher)

    expected = registry.get_module("plugins").list_plugins()
    assert panel.table.rowCount() == len(expected)
    shown = {panel.table.item(row, 0).text() for row in range(panel.table.rowCount())}
    assert shown == set(expected)


def test_rescan_button_genuinely_rescans_without_duplicating(qapp, tmp_path):
    """Real end-to-end proof of the discover() duplicate-entry fix,
    exercised through the actual UI button."""
    manager = PluginManager(plugin_dir=str(tmp_path))
    (tmp_path / "real_plugin").mkdir()

    class _Registry:
        def get_module(self, name: str):
            return manager if name == "plugins" else None

    dispatcher = CommandDispatcher()
    panel = PluginsPanel(_Registry(), dispatcher)  # type: ignore[arg-type]
    assert panel.table.rowCount() == 1

    panel.rescan_button.click()
    panel.rescan_button.click()

    assert panel.table.rowCount() == 1
    assert panel.table.item(0, 0).text() == "real_plugin"


def test_rescan_button_picks_up_a_real_newly_added_plugin(qapp, tmp_path):
    manager = PluginManager(plugin_dir=str(tmp_path))

    class _Registry:
        def get_module(self, name: str):
            return manager if name == "plugins" else None

    dispatcher = CommandDispatcher()
    panel = PluginsPanel(_Registry(), dispatcher)  # type: ignore[arg-type]
    assert panel.table.rowCount() == 0
    assert "No real plugins" in panel.status_label.text()

    (tmp_path / "new_plugin").mkdir()
    panel.rescan_button.click()

    assert panel.table.rowCount() == 1
    assert panel.table.item(0, 0).text() == "new_plugin"
    assert "1 real plugin" in panel.status_label.text()


def test_plugins_panel_honestly_discloses_when_the_real_subsystem_is_not_connected(qapp):
    class _EmptyRegistry:
        def get_module(self, name: str):
            return None

    dispatcher = CommandDispatcher()
    panel = PluginsPanel(_EmptyRegistry(), dispatcher)  # type: ignore[arg-type]

    assert not hasattr(panel, "table")
