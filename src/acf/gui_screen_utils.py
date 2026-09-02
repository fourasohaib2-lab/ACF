"""Screen-aware window sizing helper.

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

Deliberately placed at the top level of the `acf` package (not under
`acf.gui`): several windows in acf.gui/acf.dashboard already avoid
module-level imports of anything under acf.gui to dodge a real circular
import through acf/gui/__init__.py (see ClassicDashboardWindow's and
ESOCWindow's own docstrings/comments) - a plain helper with no Qt-window
dependencies of its own has no reason to risk the same trap.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget


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
    screen = window.screen()
    if screen is None:
        app = QApplication.instance()
        screen = app.primaryScreen() if app is not None else None

    if screen is None:
        window.resize(desired_width, desired_height)
        return

    available = screen.availableGeometry()
    max_width = max(1, int(available.width() * margin))
    max_height = max(1, int(available.height() * margin))

    width = min(desired_width, max_width)
    height = min(desired_height, max_height)

    window.resize(width, height)

    x = available.x() + (available.width() - width) // 2
    y = available.y() + (available.height() - height) // 2
    window.move(x, y)
