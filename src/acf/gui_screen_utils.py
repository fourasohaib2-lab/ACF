"""Screen-aware window sizing helpers.

ESOCWindow, ClassicDashboardWindow and AWCIDashboardWindow each used to call a
hardcoded ``self.resize(W, H)`` (1600x1000, 1400x900, 1500x950) with no regard
for the actual display the app is running on. On a screen smaller than that
(a laptop panel, a lower-resolution monitor, a remote desktop/VNC session),
the window opens larger than the available desktop: its edges, and sometimes
the toolbar or status bar, end up off-screen and unreachable.

`fit_window_to_screen` clamps the requested size to the screen's *available*
geometry (i.e. excluding taskbars/docks) and centers the resulting window on
it, so the dashboard always opens fully visible regardless of screen size -
while still using the full requested size on a screen big enough for it.

`fit_dialog_to_screen` (added 2026-09-05, continuing this same audit) closes
the exact same gap for this codebase's ~11 secondary `QDialog`s (settings,
HPC connection, log viewer, alerts, messages, component detail, ...), which
that first pass explicitly scoped to "main window sizes" only and left on
plain hardcoded `self.resize(W, H)` calls of their own (up to 720x560) - the
same failure mode, just smaller windows: on a small enough screen (a modest
remote-desktop/VNC session, e.g. 640x480) one of these can still open larger
than the display. Unlike a main window, a dialog usually has a `parent` -
`fit_dialog_to_screen` centers over that parent's frame when one is given and
already on screen (matching where a user expects a dialog to appear), falling
back to centering on the screen exactly like `fit_window_to_screen` otherwise.

Deliberately placed at the top level of the `acf` package (not under
`acf.gui`): several windows in acf.gui/acf.dashboard already avoid
module-level imports of anything under acf.gui to dodge a real circular
import through acf/gui/__init__.py (see ClassicDashboardWindow's and
ESOCWindow's own docstrings/comments) - a plain helper with no Qt-window
dependencies of its own has no reason to risk the same trap.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget


def _resolve_screen(window: QWidget):
    screen = window.screen()
    if screen is None:
        app = QApplication.instance()
        screen = app.primaryScreen() if app is not None else None
    return screen


def _clamp_size(desired_width: int, desired_height: int, available, margin: float) -> tuple[int, int]:
    max_width = max(1, int(available.width() * margin))
    max_height = max(1, int(available.height() * margin))
    return min(desired_width, max_width), min(desired_height, max_height)


def fit_window_to_screen(
    window: QWidget,
    desired_width: int,
    desired_height: int,
    margin: float = 0.92,
) -> None:
    """Resize ``window`` towards (desired_width, desired_height) without
    exceeding the screen it will open on, and center it there.

    Falls back to the plain requested size if no screen can be determined
    (e.g. in a headless/offscreen test environment) so this stays a no-op
    change of behaviour there.

    Args:
        window: The (top-level) widget being sized, typically a QMainWindow.
        desired_width: The size the caller would like, screen permitting.
        desired_height: Same, for height.
        margin: Fraction of the screen's available geometry the window may
            use at most (default 0.92) - leaves a small gap from the screen
            edges rather than clamping exactly to them.
    """
    screen = _resolve_screen(window)
    if screen is None:
        window.resize(desired_width, desired_height)
        return

    available = screen.availableGeometry()
    width, height = _clamp_size(desired_width, desired_height, available, margin)
    window.resize(width, height)

    x = available.x() + (available.width() - width) // 2
    y = available.y() + (available.height() - height) // 2
    window.move(x, y)


def fit_dialog_to_screen(
    dialog: QWidget,
    desired_width: int,
    desired_height: int,
    margin: float = 0.95,
) -> None:
    """Same clamp as `fit_window_to_screen`, sized for a secondary dialog.

    Centers over ``dialog.parentWidget()``'s current on-screen frame when
    there is one (clamped back inside the available screen geometry, so a
    parent sitting near an edge can't push the dialog off it) - falls back
    to centering on the screen, same as `fit_window_to_screen`, when there
    is no parent, the parent has no frame yet (not shown), or no screen can
    be determined at all (e.g. a headless/offscreen test environment).

    Args:
        dialog: The dialog being sized, typically a QDialog.
        desired_width: The size the caller would like, screen permitting.
        desired_height: Same, for height.
        margin: Fraction of the screen's available geometry the dialog may
            use at most (default 0.95 - a dialog is already modest-sized
            by design, so it needs less breathing room than a main window).
    """
    screen = _resolve_screen(dialog)
    if screen is None:
        dialog.resize(desired_width, desired_height)
        return

    available = screen.availableGeometry()
    width, height = _clamp_size(desired_width, desired_height, available, margin)
    dialog.resize(width, height)

    parent = dialog.parentWidget()
    parent_window = parent.window() if parent is not None else None
    # `isVisible()` (not just a non-null frameGeometry(), which even an
    # unshown widget can already report) is what actually distinguishes
    # "on screen somewhere real" from "never shown" here.
    parent_frame = parent_window.frameGeometry() if parent_window is not None and parent_window.isVisible() else None
    if parent_frame is not None and parent_frame.isValid() and not parent_frame.isNull():
        x = parent_frame.x() + (parent_frame.width() - width) // 2
        y = parent_frame.y() + (parent_frame.height() - height) // 2
        # Clamp back inside the available screen so a parent near an edge
        # (or a multi-monitor setup) can't push the dialog off-screen.
        x = max(available.x(), min(x, available.x() + available.width() - width))
        y = max(available.y(), min(y, available.y() + available.height() - height))
    else:
        x = available.x() + (available.width() - width) // 2
        y = available.y() + (available.height() - height) // 2

    dialog.move(x, y)
