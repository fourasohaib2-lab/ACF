"""
Atmospheric Complexity Framework (ACF)

Test suite for the real GUI-window construction path of the dashboard
(DashboardManager(window) -> Dashboard -> DashboardLayout.build() ->
MapView + docked panels), as opposed to the string/"test mode" path
already covered by test_dashboard_manager.py.

CORRECTED: this path was completely broken, with zero test coverage
anywhere to catch it:
- acf.gui.widgets.map_view.MapView() crashed on construction (wrong
  CartopyRenderer import - the canonical, canvas-required class
  instead of the canvas-optional compatibility facade). This meant
  DashboardLayout.build() - and so DashboardManager(window).initialize(),
  the real application main window's setup path - crashed too.
- Fixing that surfaced a second bug one level down:
  acf.visualization.cartopy_renderer.CartopyRenderer overrode
  create_map()/add_field()/status() for its canvas-less legacy mode,
  but not clear() - MapView.clear() crashed with
  AttributeError: 'NoneType' object has no attribute 'figure'.

See acf/gui/widgets/map_view.py and acf/visualization/cartopy_renderer.py's
own NOTE (correction) docstrings.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication, QMainWindow  # noqa: E402

from acf.dashboard.manager import DashboardManager  # noqa: E402
from acf.gui.widgets.map_view import MapView  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_map_view_constructs_and_renders_without_crashing(qapp):
    view = MapView()
    status = view.status()
    assert status["renderer"]["figure"] is True
    assert status["renderer"]["axis"] is True


def test_map_view_refresh_and_clear_do_not_crash(qapp):
    view = MapView()
    view.refresh()
    view.clear()
    status = view.status()
    assert status["renderer"]["figure"] is False
    assert status["renderer"]["axis"] is False


def test_dashboard_manager_with_a_real_window_builds_all_panels(qapp):
    window = QMainWindow()
    manager = DashboardManager(window)
    manager.initialize()

    panels = manager.dashboard.panels
    for expected in ("map", "explorer", "charts", "properties", "timeline", "console", "status"):
        assert expected in panels

    assert manager.status()["dashboard"] is True

    # Full lifecycle must not raise.
    manager.clear_project()
    manager.refresh()
    manager.shutdown()
