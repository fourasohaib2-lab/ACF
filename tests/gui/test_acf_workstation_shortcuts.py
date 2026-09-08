"""
Tests for acf.gui.dashboard.acf_workstation.ACFWorkstation's real
keyboard shortcuts (added 2026-09-04) - Ctrl+R (refresh), F11
(fullscreen), Ctrl+1..Ctrl+9/Ctrl+0 (nav by position, for the first 10
real enabled modules only - see below). Each shortcut's `.activated`
signal is triggered directly (`.emit()`) rather than via simulated key
presses - QShortcut's default WindowShortcut context requires the
hosting top-level window to be active, which is not a reliable,
portable thing to assert in a headless test environment; emitting
`.activated` directly tests exactly what each shortcut is wired to do,
without depending on window-activation timing.

NOTE (correction, 2026-09-04): `_ENABLED_MODULES` grew past 10 real
modules with the addition of "3D View" (Phase 14) - there are only 10
real single Ctrl+digit keys (1-9, 0), so `_setup_shortcuts()` honestly
caps nav shortcuts at the first 10 real modules; any further real
module (only "3D View" today) has no keyboard shortcut of its own -
still real and reachable via the nav list or the Command Palette, just
not via Ctrl+digit. Tests below assert this real, disclosed cap
exactly, not a naive 1-shortcut-per-module assumption that no longer
holds.
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


def test_one_real_nav_shortcut_per_module_capped_at_10_real_digit_keys(qapp):
    ws = ACFWorkstation()
    assert len(ws.nav_shortcuts) == min(len(_ENABLED_MODULES), 10)


def test_nav_shortcuts_use_the_real_ctrl_digit_sequence(qapp):
    ws = ACFWorkstation()
    n_shortcuts = min(len(_ENABLED_MODULES), 10)
    expected_digits = [str((i + 1) % 10) for i in range(n_shortcuts)]  # 1..9, then 0

    for shortcut, digit in zip(ws.nav_shortcuts, expected_digits, strict=True):
        assert shortcut.key() == QKeySequence(f"Ctrl+{digit}")


def test_triggering_a_nav_shortcut_switches_to_the_real_module(qapp):
    ws = ACFWorkstation()
    ws.nav_list.setCurrentRow(0)

    ws.nav_shortcuts[3].activated.emit()  # the 4th real module, Ctrl+4

    assert ws.nav_list.currentRow() == 3
    assert ws.stack.currentWidget() is ws.interactions_panel


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
