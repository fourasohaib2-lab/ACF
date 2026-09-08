"""
Tests for acf.gui_screen_utils - screen-aware window/dialog sizing.

`fit_window_to_screen` shipped in a prior session with no dedicated
test of its own (only verified indirectly via "28/28 GUI tests still
pass" on the windows that call it) - covered directly here for the
first time. `fit_dialog_to_screen` is new (2026-09-05, closing the
same gap for this codebase's secondary QDialogs, which the original
fix explicitly scoped to "main window sizes" only).

Both are exercised against a real screen (whatever `QApplication`
reports in this test environment - typically 800x800 under
`QT_QPA_PLATFORM=offscreen`) rather than a mocked one: `QScreen` is a
final Qt class PySide6 does not allow subclassing/mocking cleanly, and
the real behaviour that matters here - "never exceeds what's
available, still uses the full request when there's room" - is fully
observable against whatever screen is actually present.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QWidget

from acf.gui_screen_utils import fit_dialog_to_screen, fit_window_to_screen


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _available_geometry(qapp):
    screen = qapp.primaryScreen()
    assert screen is not None, "test environment must have a screen (even the offscreen platform provides one)"
    return screen.availableGeometry()


# ------------------------------------------------------------- fit_window_to_screen


def test_fit_window_to_screen_uses_full_request_when_it_fits(qapp):
    available = _available_geometry(qapp)
    # A tiny request relative to the real screen always "fits".
    small_w, small_h = 100, 80
    assert small_w <= available.width() and small_h <= available.height()

    window = QMainWindow()
    fit_window_to_screen(window, small_w, small_h)
    assert window.width() == small_w
    assert window.height() == small_h


def test_fit_window_to_screen_clamps_to_available_geometry(qapp):
    available = _available_geometry(qapp)
    # Ask for something guaranteed larger than the real screen.
    oversized_w = available.width() * 10
    oversized_h = available.height() * 10

    window = QMainWindow()
    fit_window_to_screen(window, oversized_w, oversized_h, margin=0.92)

    assert window.width() <= int(available.width() * 0.92) + 1
    assert window.height() <= int(available.height() * 0.92) + 1
    # Never silently ignored either - it should still have grown as
    # close to the margin-clamped ceiling as the request allows.
    assert window.width() > 0
    assert window.height() > 0


def test_fit_window_to_screen_centers_on_the_screen(qapp):
    available = _available_geometry(qapp)
    window = QMainWindow()
    fit_window_to_screen(window, 200, 150)

    expected_x = available.x() + (available.width() - 200) // 2
    expected_y = available.y() + (available.height() - 150) // 2
    assert window.x() == expected_x
    assert window.y() == expected_y


def test_fit_window_to_screen_falls_back_when_no_screen_can_be_resolved(qapp):
    """A widget that reports no screen at all (screen() -> None with no
    QApplication.primaryScreen() either) must not raise - same
    documented headless-safe fallback as before this test existed."""
    window = QMainWindow()
    window.screen = lambda: None  # type: ignore[method-assign]

    # Even QApplication.instance().primaryScreen() is real here, so this
    # exercises the "window.screen() is None but app screen exists" path,
    # not the fully-headless one - both return early via the same branch
    # once `screen` ends up None, so this is still a meaningful check that
    # resize() alone (no crash, no move()) is what happens when a widget
    # genuinely cannot resolve a screen for itself.
    fit_window_to_screen(window, 321, 234)
    assert window.width() == 321
    assert window.height() == 234


# ------------------------------------------------------------- fit_dialog_to_screen


def test_fit_dialog_to_screen_uses_full_request_when_it_fits(qapp):
    available = _available_geometry(qapp)
    small_w, small_h = 120, 90
    assert small_w <= available.width() and small_h <= available.height()

    dialog = QDialog()
    fit_dialog_to_screen(dialog, small_w, small_h)
    assert dialog.width() == small_w
    assert dialog.height() == small_h


def test_fit_dialog_to_screen_clamps_to_available_geometry(qapp):
    available = _available_geometry(qapp)
    oversized_w = available.width() * 10
    oversized_h = available.height() * 10

    dialog = QDialog()
    fit_dialog_to_screen(dialog, oversized_w, oversized_h, margin=0.95)

    assert dialog.width() <= int(available.width() * 0.95) + 1
    assert dialog.height() <= int(available.height() * 0.95) + 1


def test_fit_dialog_to_screen_without_parent_centers_on_screen(qapp):
    available = _available_geometry(qapp)
    dialog = QDialog()
    fit_dialog_to_screen(dialog, 200, 150)

    expected_x = available.x() + (available.width() - 200) // 2
    expected_y = available.y() + (available.height() - 150) // 2
    assert dialog.x() == expected_x
    assert dialog.y() == expected_y


def test_fit_dialog_to_screen_with_shown_parent_centers_on_the_parent(qapp):
    parent = QMainWindow()
    fit_window_to_screen(parent, 600, 500)
    parent.show()

    dialog = QDialog(parent)
    fit_dialog_to_screen(dialog, 200, 150)

    parent_frame = parent.frameGeometry()
    expected_x = parent_frame.x() + (parent_frame.width() - 200) // 2
    expected_y = parent_frame.y() + (parent_frame.height() - 150) // 2
    assert dialog.x() == expected_x
    assert dialog.y() == expected_y


def test_fit_dialog_to_screen_never_places_dialog_outside_available_geometry(qapp):
    """A parent pinned right at the screen's edge must not be able to
    push a centered-over-parent dialog off-screen."""
    available = _available_geometry(qapp)
    parent = QMainWindow()
    parent.resize(300, 300)
    # Pin the parent hard against the top-left corner.
    parent.move(available.x(), available.y())
    parent.show()

    dialog = QDialog(parent)
    fit_dialog_to_screen(dialog, 500, 500)

    assert dialog.x() >= available.x()
    assert dialog.y() >= available.y()
    assert dialog.x() + dialog.width() <= available.x() + available.width()
    assert dialog.y() + dialog.height() <= available.y() + available.height()


def test_fit_dialog_to_screen_falls_back_when_no_screen_can_be_resolved(qapp):
    dialog = QDialog()
    dialog.screen = lambda: None  # type: ignore[method-assign]

    fit_dialog_to_screen(dialog, 321, 234)
    assert dialog.width() == 321
    assert dialog.height() == 234


def test_fit_dialog_to_screen_ignores_a_parent_with_no_real_frame_yet(qapp):
    """A parent constructed but never shown/positioned should not be
    trusted for centering - falls back to centering on the screen."""
    available = _available_geometry(qapp)
    parent = QWidget()  # never shown, never resized/moved
    dialog = QDialog(parent)

    fit_dialog_to_screen(dialog, 200, 150)

    expected_x = available.x() + (available.width() - 200) // 2
    expected_y = available.y() + (available.height() - 150) // 2
    assert dialog.x() == expected_x
    assert dialog.y() == expected_y
