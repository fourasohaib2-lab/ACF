"""
Atmospheric Complexity Framework (ACF)

Test suite for acf.gui.map.map_camera.MapCamera and
acf.gui.map.map_navigation.NavigationMixin.

CORRECTED: MapCamera's entire method set (__init__, initialize,
set_center, center, move, pan, zoom, set_zoom, zoom_in, zoom_out,
set_projection, projection, set_extent, fit_world, fit_extent, reset,
status) was defined at MODULE level due to a dedent - none of it was
actually part of the class body. MapCamera() constructed (falling
back to QObject's own __init__) but had none of its own methods at
all: MapCamera().set_center(1.0, 2.0) raised "AttributeError:
'MapCamera' object has no attribute 'set_center'". Fixing that
surfaced a second, previously-masked bug: NavigationMixin.fit_extent()
passed its `extent` argument straight through as a single positional
argument to MapCamera.set_extent(), which requires 4 separate
positional arguments (west, east, south, north) - every call to
fit_extent()/fit_world() raised "TypeError: set_extent() missing 3
required positional arguments".

Neither class was used anywhere else in the codebase or covered by
any test before this - fixed anyway, matching this session's "fix a
broken component even if currently unused" precedent (see
acf.models.base_model.BaseWeatherModel's own NOTE (correction)).

See map_camera.py and map_navigation.py's own NOTE (correction)
docstrings.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from acf.gui.map.map_camera import MapCamera  # noqa: E402
from acf.gui.map.map_navigation import NavigationMixin  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeMapCanvas(NavigationMixin):
    """Smallest object exercising NavigationMixin against a real MapCamera."""

    def __init__(self):
        self.camera = MapCamera()
        self.refresh_count = 0

    def refresh(self):
        self.refresh_count += 1


def test_map_camera_has_its_own_methods(qapp):
    cam = MapCamera()
    assert cam.center() == (0.0, 0.0)
    assert cam.zoom() == 1.0
    assert cam.projection() == "PlateCarree"


def test_map_camera_set_center_and_pan(qapp):
    cam = MapCamera()
    cam.set_center(10.0, 20.0)
    assert cam.center() == (10.0, 20.0)
    cam.pan(1.0, -1.0)
    assert cam.center() == (11.0, 19.0)


def test_map_camera_zoom_is_clamped(qapp):
    cam = MapCamera()
    cam.set_zoom(1000.0)
    assert cam.zoom() == cam.max_zoom
    cam.set_zoom(-5.0)
    assert cam.zoom() == cam.min_zoom
    cam.zoom_in()
    assert cam.zoom() > cam.min_zoom


def test_map_camera_set_extent_requires_four_values(qapp):
    cam = MapCamera()
    cam.set_extent(-10, 10, -20, 20)
    assert cam.extent == [-10, 10, -20, 20]


def test_map_camera_reset(qapp):
    cam = MapCamera()
    cam.set_center(50.0, 50.0)
    cam.set_zoom(10.0)
    cam.reset()
    assert cam.center() == (0.0, 0.0)
    assert cam.zoom() == 1.0


def test_navigation_mixin_fit_world_and_fit_extent(qapp):
    canvas = _FakeMapCanvas()
    canvas.fit_world()
    assert canvas.current_extent() == [-180, 180, -90, 90]

    canvas.fit_extent((-30, 30, -40, 40))
    assert canvas.current_extent() == [-30, 30, -40, 40]
    assert canvas.refresh_count == 2


def test_navigation_mixin_pan_and_zoom(qapp):
    canvas = _FakeMapCanvas()
    canvas.pan(5, -5)
    assert canvas.current_center() == (5.0, -5.0)

    canvas.zoom_in()
    assert canvas.current_zoom() > 1.0

    canvas.reset_view()
    assert canvas.current_center() == (0.0, 0.0)
    assert canvas.current_zoom() == 1.0
