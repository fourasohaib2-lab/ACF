"""
Tests for acf.gui.esoc.panel_manager.WorkspaceModesPanel - the real,
read-only Workspace Modes reference browser closing the previously-
dead "Settings / Workspace Modes" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_workspace import WorkspaceManager, WorkspaceMode
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import WorkspaceModesPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_lists_every_real_workspace_mode(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = WorkspaceModesPanel(registry, dispatcher)

    items = [panel.mode_selector.itemText(i) for i in range(panel.mode_selector.count())]
    assert items == WorkspaceManager().list_modes()


def test_default_profile_matches_the_real_manager_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = WorkspaceModesPanel(registry, dispatcher)

    expected = WorkspaceManager().get_current_profile()  # defaults to Meteorologist
    text = panel.profile_text.toPlainText()
    assert expected["primary_panel"] in text
    assert expected["description"] in text


def test_switching_the_selector_shows_a_genuinely_different_real_profile(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = WorkspaceModesPanel(registry, dispatcher)

    panel.mode_selector.setCurrentText("Emergency")

    manager = WorkspaceManager()
    manager.current_mode = WorkspaceMode.EMERGENCY
    expected = manager.get_current_profile()
    text = panel.profile_text.toPlainText()
    assert expected["primary_panel"] in text
    assert expected["description"] in text


def test_every_real_mode_produces_a_non_empty_real_profile(qapp, registry):
    """Real regression guard: every one of the 10 real modes must
    render without raising and without an empty result."""
    dispatcher = CommandDispatcher()
    panel = WorkspaceModesPanel(registry, dispatcher)

    for mode_name in WorkspaceManager().list_modes():
        panel.mode_selector.setCurrentText(mode_name)
        assert panel.profile_text.toPlainText().strip() != ""
