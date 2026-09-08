"""
Real end-to-end regression guard tying this session's responsive-sizing
fixes to this exact codebase's own real headless/HPC deployment
fallback: `acf.gui.bootstrap.configure_runtime()` auto-configures
`QT_QPA_PLATFORM=vnc:size=1280x720:port=5910` whenever no DISPLAY/
WAYLAND_DISPLAY is available (an HPC login/compute node, this exact
sandbox included) - a *real* screen size this app is deployed against,
not a hypothetical one.

Before this session's fixes, none of the 3 main windows actually fit
that screen once shown:
- ESOCWindow's own enforced minimum was ~1314x1053 (QTabWidget floored
  at its largest of 44 tabs + oversized ViewManager combos) - wider AND
  taller than 1280x720.
- ACFWorkstationWindow's was ~1119x978 (QStackedWidget floored at its
  largest of 15 Lab panels) - taller than 720.
- AWCIDashboardWindow's was ~1489x1064 (its own dense real map/chart
  layout, no "wrong page" involved) - both dimensions exceeded.

`fit_window_to_screen`'s own resize()/margin clamp cannot fix any of
this alone: Qt floors a QMainWindow's actual minimum size to its content
layout's, regardless of what size was requested - only removing that
FLOOR (this session's actual fixes: CurrentPageStackedWidget/
CurrentPageTabWidget, the ViewManager combo fix, and wrapping each of
the 3 windows' heavy content in a QScrollArea) makes the screen clamp
truly effective.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_window import ACFWorkstationWindow
from acf.gui.dashboard.awci_window import AWCIDashboardWindow
from acf.gui.esoc.esoc_window import ESOCWindow
from acf.gui_screen_utils import fit_window_to_screen

#: This session's own tests/exploration confirmed acf.gui.bootstrap.py
#: hardcodes this exact size for its auto-configured headless-fallback
#: VNC platform - kept as a literal here (not imported) so this test
#: fails loudly, rather than silently tracking a change, if that real
#: fallback size is ever edited without re-checking these 3 windows.
_HPC_VNC_FALLBACK_SIZE = (1280, 720)

#: Each window's own real desired size, as passed to fit_window_to_screen
#: at construction - see each window's own __init__.
_WINDOWS_AND_DESIRED_SIZE = [
    (ESOCWindow, (1600, 1000)),
    (ACFWorkstationWindow, (1600, 1000)),
    (AWCIDashboardWindow, (1500, 950)),
]


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FixedSizeScreen:
    """Minimal stand-in for the QScreen this exact VNC fallback
    advertises - not a mock of QScreen itself (a final Qt class), just
    the two methods gui_screen_utils.fit_window_to_screen calls."""

    def __init__(self, width: int, height: int) -> None:
        self._rect = QRect(0, 0, width, height)

    def availableGeometry(self) -> QRect:
        return self._rect

    def geometry(self) -> QRect:
        return self._rect


@pytest.mark.parametrize(("window_cls", "desired_size"), _WINDOWS_AND_DESIRED_SIZE)
def test_main_window_fits_the_real_hpc_vnc_fallback_screen(qapp, window_cls, desired_size):
    width, height = _HPC_VNC_FALLBACK_SIZE
    window = window_cls()
    window.screen = lambda: _FixedSizeScreen(width, height)  # type: ignore[method-assign]
    fit_window_to_screen(window, *desired_size)
    window.show()

    assert window.width() <= width, (
        f"{window_cls.__name__} is {window.width()}px wide - wider than the "
        f"{width}px this codebase's own bootstrap.py auto-configures for a "
        "headless/HPC VNC session"
    )
    assert window.height() <= height, (
        f"{window_cls.__name__} is {window.height()}px tall - taller than the "
        f"{height}px this codebase's own bootstrap.py auto-configures for a "
        "headless/HPC VNC session"
    )
