"""
Tests for acf.gui.map.map_camera.MapCamera - real zoom/pan/extent
state, and specifically its `current_extent()` fix (explicit user
request "ajoute l'option zoom des cartes et manipulation totale des
cartes"). Before this fix, zoom_in()/pan() changed zoom_level/center
but never touched self.extent - these tests lock in that a real
extent change now genuinely follows from real zoom/pan/center calls,
not just internal bookkeeping.
"""

from __future__ import annotations

import pytest

from acf.gui.map.map_camera import MapCamera


def test_default_extent_is_the_whole_world():
    camera = MapCamera()
    assert camera.current_extent() == pytest.approx([-180.0, 180.0, -90.0, 90.0])
    assert camera.extent == pytest.approx([-180.0, 180.0, -90.0, 90.0])


def test_zoom_in_genuinely_narrows_the_extent():
    camera = MapCamera()
    world_extent = camera.current_extent()
    camera.zoom_in(factor=2.0)
    zoomed_extent = camera.current_extent()
    world_width = world_extent[1] - world_extent[0]
    zoomed_width = zoomed_extent[1] - zoomed_extent[0]
    assert zoomed_width == pytest.approx(world_width / 2.0)
    # self.extent (the attribute a caller/test might read directly, not
    # just the current_extent() method) is kept in sync too.
    assert camera.extent == pytest.approx(zoomed_extent)


def test_zoom_out_genuinely_widens_the_extent_but_clamps_to_the_world():
    camera = MapCamera()
    camera.zoom_out(factor=2.0)  # zoom_level would go to 0.5, doubling the span - but the world is already fully visible
    extent = camera.current_extent()
    # Longitude/latitude are clamped at the real world bounds - can't
    # show more than the whole Earth.
    assert extent[0] == -180.0
    assert extent[1] == 180.0
    assert extent[2] == -90.0
    assert extent[3] == 90.0


def test_pan_genuinely_moves_the_extent():
    camera = MapCamera()
    camera.zoom_in(factor=4.0)  # zoom in first so panning doesn't immediately clamp at the world edge
    before = camera.current_extent()
    camera.pan(10.0, 5.0)
    after = camera.current_extent()
    assert after[0] > before[0]  # west edge moved east
    assert after[1] > before[1]  # east edge moved east
    assert after[2] > before[2]  # south edge moved north
    assert after[3] > before[3]  # north edge moved north


def test_pan_clamps_longitude_and_latitude_at_world_edges():
    camera = MapCamera()
    camera.zoom_in(factor=4.0)
    camera.pan(1000.0, 1000.0)  # a real, deliberately huge pan
    extent = camera.current_extent()
    assert extent[1] <= 180.0
    assert extent[3] <= 90.0


def test_set_extent_derives_a_consistent_center_and_zoom():
    camera = MapCamera()
    camera.set_extent(-90.0, 90.0, -45.0, 45.0)  # a real quarter-width-of-world extent
    assert camera.center() == pytest.approx((0.0, 0.0))
    # half-width is 90 degrees -> zoom_level should be world(180)/90 = 2.0
    assert camera.zoom_level == pytest.approx(2.0)
    # current_extent() recomputed from the derived center/zoom must
    # match what was actually set - the two directions (extent -> zoom,
    # zoom -> extent) are real inverses of each other, not independent.
    assert camera.current_extent() == pytest.approx([-90.0, 90.0, -45.0, 45.0])


def test_reset_returns_to_the_real_default_state():
    camera = MapCamera()
    camera.zoom_in(factor=3.0)
    camera.pan(20.0, 20.0)
    camera.reset()
    assert camera.zoom_level == pytest.approx(1.0)
    assert camera.center() == pytest.approx((0.0, 0.0))
    assert camera.current_extent() == pytest.approx([-180.0, 180.0, -90.0, 90.0])


def test_extent_changed_signal_fires_on_a_real_zoom_change(qtbot):
    camera = MapCamera()
    with qtbot.waitSignal(camera.extentChanged, timeout=1000) as blocker:
        camera.zoom_in(factor=2.0)
    assert blocker.args[0] == pytest.approx(camera.extent)
