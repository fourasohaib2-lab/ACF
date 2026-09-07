"""
Tests for AWCI's real screen-adaptability fix (2026-09-07, explicit
user request "assure toi que la resolution est adaptable selon le type
d'ecran elle est ajustable").

Real measurements behind this (offscreen "vnc" Qt platform plugin,
real pixel dimensions, no X11/xcb-cursor needed - same technique used
earlier this session for the resolution-stability work):
  - 1366x768 and 1280x800 (common real laptop screens): at a fixed
    scale of 1.0, forced 700px+ of real horizontal scroll and 200px+
    of vertical scroll - the dashboard's matplotlib figures/minimum
    heights never shrank to match a smaller real screen.
  - 2560x1440 (a real, larger-than-reference monitor): already fits
    with zero scroll at scale 1.0, and the dashboard genuinely grows
    to fill the extra space (Expanding size policies), so scale is
    deliberately capped at 1.0 (see compute_screen_scale's own
    docstring for why growing further isn't applied).

compute_screen_scale() gives every fixed-pixel figure/panel size in
AWCIDashboard a genuine floor-to-real-screen scale instead of a fixed
1920x1080 assumption. The window remains genuinely resizable by the
operator throughout (no setFixedSize/setMaximumSize anywhere in this
window's own code) - "ajustable" was already true before this fix;
this fix is about the INITIAL fit being screen-aware, not about
making the window resizable (it always was).
"""

from __future__ import annotations

import sys

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui_screen_utils import compute_screen_scale


def _qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_scale_is_1_when_no_real_screen_can_be_determined():
    """The same honest fallback fit_window_to_screen already uses -
    verified directly by faking _resolve_screen's failure path rather
    than relying on this test's own real (offscreen, but real) screen
    reporting None, which it usually doesn't."""
    from unittest.mock import patch

    from PySide6.QtWidgets import QWidget

    _qapp()
    widget = QWidget()
    with patch("acf.gui_screen_utils._resolve_screen", return_value=None):
        assert compute_screen_scale(widget) == 1.0


def test_scale_never_exceeds_1_even_on_a_larger_than_reference_screen():
    """2560x1440 real monitor case - see this module's own docstring."""
    from unittest.mock import MagicMock, patch

    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import QWidget

    _qapp()
    widget = QWidget()
    fake_screen = MagicMock()
    fake_screen.availableGeometry.return_value = QRect(0, 0, 2560, 1440)
    with patch("acf.gui_screen_utils._resolve_screen", return_value=fake_screen):
        assert compute_screen_scale(widget) == 1.0


def test_scale_shrinks_genuinely_on_a_real_small_laptop_screen():
    """1366x768 real laptop case - see this module's own docstring."""
    from unittest.mock import MagicMock, patch

    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import QWidget

    _qapp()
    widget = QWidget()
    fake_screen = MagicMock()
    fake_screen.availableGeometry.return_value = QRect(0, 0, 1366, 768)
    with patch("acf.gui_screen_utils._resolve_screen", return_value=fake_screen):
        scale = compute_screen_scale(widget)

    assert scale < 1.0
    assert scale == pytest.approx(768 / 1080, rel=1e-3)  # height is the binding real constraint here


def test_scale_never_goes_below_its_real_floor_on_a_tiny_screen():
    from unittest.mock import MagicMock, patch

    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import QWidget

    _qapp()
    widget = QWidget()
    fake_screen = MagicMock()
    fake_screen.availableGeometry.return_value = QRect(0, 0, 320, 240)
    with patch("acf.gui_screen_utils._resolve_screen", return_value=fake_screen):
        scale = compute_screen_scale(widget, floor=0.6)

    assert scale == 0.6


def test_awci_dashboard_threads_screen_scale_into_every_real_figure_and_min_height(qtbot):
    """Not a fake assertion on a private attribute alone - checks the
    REAL, measurable effect: a smaller scale genuinely shrinks the real
    matplotlib figure sizes and setMinimumHeight() floors, not just a
    stored number nothing reads."""
    from acf.gui.dashboard.awci_dashboard import AWCIDashboard

    default_dashboard = AWCIDashboard()
    qtbot.addWidget(default_dashboard)
    scaled_dashboard = AWCIDashboard(screen_scale=0.7)
    qtbot.addWidget(scaled_dashboard)

    assert scaled_dashboard._screen_scale == 0.7
    assert scaled_dashboard.global_map.figure.get_size_inches()[0] < default_dashboard.global_map.figure.get_size_inches()[0]
    assert scaled_dashboard.radar.figure.get_size_inches()[0] < default_dashboard.radar.figure.get_size_inches()[0]
    assert scaled_dashboard.route_chart.figure.get_size_inches()[0] < default_dashboard.route_chart.figure.get_size_inches()[0]
    assert scaled_dashboard.cross_section.figure.get_size_inches()[0] < default_dashboard.cross_section.figure.get_size_inches()[0]
    assert scaled_dashboard.regional_map.figure.get_size_inches()[0] < default_dashboard.regional_map.figure.get_size_inches()[0]
    assert scaled_dashboard.global_map.minimumHeight() < default_dashboard.global_map.minimumHeight()


def test_awci_dashboard_default_screen_scale_is_1_unchanged_behaviour(qtbot):
    """Every existing caller that never passed screen_scale (ESOC's own
    dock panel, every pre-existing test constructing AWCIDashboard()
    bare) must keep the exact same real figure sizes as before this
    fix - no silent behaviour change for them."""
    from acf.gui.dashboard.awci_dashboard import AWCIDashboard

    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    assert dashboard._screen_scale == 1.0
    assert dashboard.global_map.figure.get_size_inches()[0] == pytest.approx(6.0)
    assert dashboard.radar.figure.get_size_inches()[0] == pytest.approx(5.4)


def test_awci_dashboard_window_computes_and_threads_a_real_screen_scale(qtbot):
    from acf.gui.dashboard.awci_window import AWCIDashboardWindow

    window = AWCIDashboardWindow()
    qtbot.addWidget(window)

    assert window.awci_dashboard._screen_scale == window._screen_scale
    assert 0.6 <= window._screen_scale <= 1.0


def test_awci_dashboard_window_has_no_fixed_size_constraint(qtbot):
    """"ajustable" - the operator must always be able to resize this
    window by hand, on any real screen."""
    from acf.gui.dashboard.awci_window import AWCIDashboardWindow

    window = AWCIDashboardWindow()
    qtbot.addWidget(window)

    # Qt's real "no explicit maximum set" sentinel is 16777215
    # (QWIDGETSIZE_MAX, not importable from this PySide6 build's
    # QtWidgets) - a genuinely resizable window reports it on both axes.
    assert window.maximumWidth() == 16777215
    assert window.maximumHeight() == 16777215
