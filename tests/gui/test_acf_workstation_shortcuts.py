"""
Tests for acf.gui.dashboard.acf_workstation.ACFWorkstation's real
keyboard shortcuts (added 2026-09-04) - Ctrl+R (refresh), F11
(fullscreen), Ctrl+1..Ctrl+9/Ctrl+0 (nav by position). Each shortcut's
`.activated` signal is triggered directly (`.emit()`) rather than via
simulated key presses - QShortcut's default WindowShortcut context
requires the hosting top-level window to be active, which is not a
reliable, portable thing to assert in a headless test environment;
emitting `.activated` directly tests exactly what each shortcut is
wired to do, without depending on window-activation timing.
"""

from __future__ import annotations

import pytest
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation import ACFWorkstation, _ENABLED_MODULES


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_exactly_one_real_nav_shortcut_per_real_enabled_module(qapp):
    ws = ACFWorkstation()
    assert len(ws.nav_shortcuts) == len(_ENABLED_MODULES)


def test_nav_shortcuts_use_the_real_ctrl_digit_sequence(qapp):
    ws = ACFWorkstation()
    expected_digits = [str((i + 1) % 10) for i in range(len(_ENABLED_MODULES))]  # 1..9, then 0

    for shortcut, digit in zip(ws.nav_shortcuts, expected_digits, strict=True):
        assert shortcut.key() == QKeySequence(f"Ctrl+{digit}")


def test_triggering_a_nav_shortcut_switches_to_the_real_module(qapp):
    ws = ACFWorkstation()
    ws.nav_list.setCurrentRow(0)

    ws.nav_shortcuts[3].activated.emit()  # the 4th real module, Ctrl+4

    assert ws.nav_list.currentRow() == 3
    assert ws.stack.currentWidget() is ws.microphysics_panel


def test_ctrl_r_shortcut_calls_the_real_refresh(qapp, monkeypatch):
    ws = ACFWorkstation()
    called = {"n": 0}
    monkeypatch.setattr(ws, "refresh", lambda: called.__setitem__("n", called["n"] + 1))

    ws.shortcut_run.activated.emit()

    assert called["n"] == 1


def test_f11_shortcut_calls_the_real_fullscreen_toggle(qapp, monkeypatch):
    ws = ACFWorkstation()
    called = {"n": 0}
    monkeypatch.setattr(ws, "_toggle_fullscreen", lambda: called.__setitem__("n", called["n"] + 1))

    ws.shortcut_fullscreen.activated.emit()

    assert called["n"] == 1
