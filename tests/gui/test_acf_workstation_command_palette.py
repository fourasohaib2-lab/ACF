"""
Tests for acf.gui.dashboard.acf_workstation_command_palette.
CommandPaletteDialog (added 2026-09-04) and ACFWorkstation's own Ctrl+K
wiring/command list.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation import ACFWorkstation, _ENABLED_MODULES
from acf.gui.dashboard.acf_workstation_command_palette import CommandPaletteDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# --------------------------------------------------------- CommandPaletteDialog itself


def test_starts_listing_every_real_command(qapp):
    calls: list[str] = []
    commands = [("Alpha", lambda: calls.append("alpha")), ("Beta", lambda: calls.append("beta"))]
    dialog = CommandPaletteDialog(commands)

    assert dialog.result_list.count() == 2
    assert {dialog.result_list.item(i).text() for i in range(2)} == {"Alpha", "Beta"}


def test_filter_is_real_case_insensitive_substring_matching(qapp):
    commands = [("Run", lambda: None), ("Go to Overview", lambda: None), ("Go to Dynamics", lambda: None)]
    dialog = CommandPaletteDialog(commands)

    dialog.search_input.setText("dynamics")

    assert dialog.result_list.count() == 1
    assert dialog.result_list.item(0).text() == "Go to Dynamics"


def test_run_command_executes_the_real_callback_and_closes(qapp):
    calls: list[str] = []
    commands = [("Alpha", lambda: calls.append("alpha"))]
    dialog = CommandPaletteDialog(commands)

    dialog.run_command("Alpha")

    assert calls == ["alpha"]
    assert dialog.isVisible() is False


def test_return_pressed_activates_the_currently_selected_command(qapp):
    calls: list[str] = []
    commands = [("Alpha", lambda: calls.append("alpha")), ("Beta", lambda: calls.append("beta"))]
    dialog = CommandPaletteDialog(commands)
    dialog.search_input.setText("beta")

    dialog.search_input.returnPressed.emit()

    assert calls == ["beta"]


def test_set_commands_refreshes_the_real_filtered_list(qapp):
    dialog = CommandPaletteDialog([("Alpha", lambda: None)])
    assert dialog.result_list.count() == 1

    dialog.set_commands([("Alpha", lambda: None), ("Beta", lambda: None)])

    assert dialog.result_list.count() == 2


# --------------------------------------------------------- ACFWorkstation wiring


def test_ctrl_k_shortcut_opens_the_real_palette(qapp):
    ws = ACFWorkstation()
    assert ws._command_palette is None

    ws.shortcut_command_palette.activated.emit()

    assert ws._command_palette is not None
    assert ws._command_palette.isVisible() is True


def test_palette_command_list_includes_run_fullscreen_and_every_module(qapp):
    ws = ACFWorkstation()

    commands = ws._build_palette_commands()

    labels = [label for label, _callback in commands]
    assert "Run" in labels
    assert "Toggle Fullscreen" in labels
    for name in _ENABLED_MODULES:
        assert f"Go to {name}" in labels


def test_running_a_go_to_command_switches_the_real_nav(qapp):
    ws = ACFWorkstation()
    ws.nav_list.setCurrentRow(0)
    commands = dict(ws._build_palette_commands())

    commands["Go to Microphysics"]()

    assert ws.nav_list.currentRow() == _ENABLED_MODULES.index("Microphysics")


def test_running_the_run_command_calls_the_real_refresh(qapp, monkeypatch):
    ws = ACFWorkstation()
    called = {"n": 0}
    monkeypatch.setattr(ws, "refresh", lambda: called.__setitem__("n", called["n"] + 1))
    commands = dict(ws._build_palette_commands())

    commands["Run"]()

    assert called["n"] == 1


def test_opening_the_palette_twice_reuses_the_same_real_dialog(qapp):
    ws = ACFWorkstation()

    ws._open_command_palette()
    first = ws._command_palette
    ws._open_command_palette()

    assert ws._command_palette is first
