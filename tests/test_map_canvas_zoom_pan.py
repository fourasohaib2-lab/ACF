"""
Tests for acf.gui.map.map_canvas.MapCanvas's real interactive zoom/pan
(explicit user request "ajoute l'option zoom des cartes et
manipulation totale des cartes").

Dispatches real Qt events (QWheelEvent/QKeyEvent/QMouseEvent) via
QApplication.sendEvent() to `canvas.canvas` - the actual embedded
FigureCanvasQTAgg child widget Qt delivers real mouse/wheel/keyboard
input to - not by calling MapCanvas's own event-handler methods
directly. This distinction matters and is not just test pedantry: an
earlier version of this wiring passed every test that called
`canvas.wheelEvent(event)` directly, but a real scroll over the
embedded canvas never reached it at all (Qt event delivery targets the
widget under the cursor, and MapCanvas.canvas is a child covering the
whole panel) - only caught by testing through the real event-filter
path, which is what these tests do.
"""

from __future__ import annotations

import cartopy.crs as ccrs
import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QApplication

from acf.gui.map.map_canvas import MapCanvas


def _send_wheel(canvas: MapCanvas, delta_y: int) -> None:
    event = QWheelEvent(
        QPointF(10, 10),
        QPointF(10, 10),
        QPoint(0, 0),
        QPoint(0, delta_y),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    assert QApplication.sendEvent(canvas.canvas, event)


def _send_key(canvas: MapCanvas, key: Qt.Key) -> None:
    event = QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier)
    assert QApplication.sendEvent(canvas.canvas, event)


def _send_mouse(canvas: MapCanvas, event_type: QEvent.Type, pos: QPointF, button: Qt.MouseButton, buttons: Qt.MouseButton) -> None:
    event = QMouseEvent(event_type, pos, button, buttons, Qt.KeyboardModifier.NoModifier)
    assert QApplication.sendEvent(canvas.canvas, event)


def test_real_scroll_over_the_embedded_canvas_genuinely_zooms_in(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    before = canvas.camera.current_extent()
    _send_wheel(canvas, 120)  # positive angleDelta = scroll up = zoom in
    after = canvas.camera.current_extent()
    assert (after[1] - after[0]) < (before[1] - before[0])  # real narrowing = real zoom in


def test_real_scroll_down_genuinely_zooms_out_after_zooming_in(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    _send_wheel(canvas, 120)
    zoomed_in = canvas.camera.current_extent()
    _send_wheel(canvas, -120)
    zoomed_out = canvas.camera.current_extent()
    assert (zoomed_out[1] - zoomed_out[0]) > (zoomed_in[1] - zoomed_in[0])


def test_real_keyboard_arrow_keys_genuinely_pan(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    _send_wheel(canvas, 120)  # zoom in first so a pan isn't immediately clamped at the world edge
    before = canvas.camera.current_extent()
    _send_key(canvas, Qt.Key.Key_Right)
    after = canvas.camera.current_extent()
    assert after[0] > before[0]
    assert after[1] > before[1]


def test_real_keyboard_plus_key_zooms_in(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    before = canvas.camera.current_extent()
    _send_key(canvas, Qt.Key.Key_Plus)
    zoomed = canvas.camera.current_extent()
    assert (zoomed[1] - zoomed[0]) < (before[1] - before[0])


def test_real_double_click_resets_to_the_whole_world_without_crashing(qtbot):
    """Real regression guard: applying MapCamera's exact +/-180/+/-90
    world extent straight to this canvas's default Mercator-projected
    GeoAxes raised a real 'Axis limits cannot be NaN or Inf' error
    (Mercator's genuine singularity at the poles/antimeridian) before
    _apply_camera_extent()'s Mercator-safe display clamp was added -
    found by running this exact sequence, not a hypothetical case."""
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    _send_wheel(canvas, 120)
    _send_key(canvas, Qt.Key.Key_Right)
    _send_mouse(canvas, QEvent.Type.MouseButtonDblClick, QPointF(10, 10), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton)
    assert canvas.camera.current_extent() == pytest.approx([-180.0, 180.0, -90.0, 90.0])
    extent = canvas.axes.get_extent()
    assert all(abs(v) < float("inf") for v in extent)


def test_real_mouse_drag_over_the_embedded_canvas_genuinely_pans(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    _send_wheel(canvas, 120)  # zoom in so the drag isn't immediately clamped
    _send_mouse(canvas, QEvent.Type.MouseButtonPress, QPointF(100, 100), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton)
    before = canvas.camera.current_extent()
    _send_mouse(canvas, QEvent.Type.MouseMove, QPointF(150, 100), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton)
    after = canvas.camera.current_extent()
    assert after != before  # a real left-button drag genuinely moved the camera


def test_on_canvas_zoom_buttons_are_real_and_wired(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    before = canvas.camera.current_extent()
    qtbot.mouseClick(canvas.zoom_in_button, Qt.MouseButton.LeftButton)
    after = canvas.camera.current_extent()
    assert (after[1] - after[0]) < (before[1] - before[0])
    qtbot.mouseClick(canvas.reset_view_button, Qt.MouseButton.LeftButton)
    assert canvas.camera.current_extent() == pytest.approx([-180.0, 180.0, -90.0, 90.0])


def test_set_projection_preserves_zoom_state_instead_of_silently_resetting(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    _send_wheel(canvas, 120)
    zoomed_extent = canvas.camera.current_extent()
    canvas.set_projection("Robinson")
    assert canvas.camera.current_extent() == pytest.approx(zoomed_extent)
    assert isinstance(canvas.projection_manager.current_crs, ccrs.Robinson)
