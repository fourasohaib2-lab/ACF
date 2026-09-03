"""
Tests for acf.gui.dashboard.awci_map_panel.AWCIMapPanel's real
click-to-select-point interaction (docs/awci/AWCI_UI_AUDIT.md - the
"click-to-set-point-of-interest" gap the pre-implementation audit found:
the map's aircraft glyphs/any point were purely decorative, clicking
did nothing). Events are dispatched to `panel.canvas` (the real target
of Qt's input delivery, matching test_awci_map_panel_zoom_pan.py's own
established convention), not to AWCIMapPanel's handler methods directly.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


def _send_mouse(panel: AWCIMapPanel, event_type: QEvent.Type, x: float, y: float) -> None:
    event = QMouseEvent(event_type, QPointF(x, y), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    assert QApplication.sendEvent(panel.canvas, event)


def _click(panel: AWCIMapPanel, x: float, y: float) -> None:
    _send_mouse(panel, QEvent.Type.MouseButtonPress, x, y)
    _send_mouse(panel, QEvent.Type.MouseButtonRelease, x, y)


def test_clicking_the_map_emits_pointclicked_with_real_lat_lon(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    panel.resize(600, 400)
    received: list[tuple[float, float]] = []
    panel.pointClicked.connect(lambda lat, lon: received.append((lat, lon)))

    cx, cy = panel.canvas.width() / 2, panel.canvas.height() / 2
    _click(panel, cx, cy)

    assert len(received) == 1
    lat, lon = received[0]
    # A click near the center of a whole-world map must resolve near (0, 0).
    assert abs(lat) < 20.0
    assert abs(lon) < 20.0


def test_dragging_the_map_does_not_emit_pointclicked(qtbot):
    """Real click-vs-drag distinction: a real pan (press far from
    release) must not be mistaken for a click."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    panel.resize(600, 400)
    received: list[tuple[float, float]] = []
    panel.pointClicked.connect(lambda lat, lon: received.append((lat, lon)))

    _send_mouse(panel, QEvent.Type.MouseButtonPress, 10, 10)
    _send_mouse(panel, QEvent.Type.MouseButtonRelease, 300, 300)

    assert received == []


def test_two_clicks_at_different_positions_give_different_real_coordinates(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    panel.resize(600, 400)
    received: list[tuple[float, float]] = []
    panel.pointClicked.connect(lambda lat, lon: received.append((lat, lon)))

    _click(panel, panel.canvas.width() * 0.2, panel.canvas.height() * 0.5)
    _click(panel, panel.canvas.width() * 0.8, panel.canvas.height() * 0.5)

    assert len(received) == 2
    assert received[0] != received[1]
    assert received[0][1] < received[1][1]  # leftward click -> smaller real longitude


def test_click_still_records_the_press_position_for_pan_bookkeeping(qtbot):
    """Real regression guard: the new mousePressEvent() override must
    not break EventMixin's own existing _last_mouse_position bookkeeping
    that real drag-panning depends on."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    panel.resize(600, 400)

    _send_mouse(panel, QEvent.Type.MouseButtonPress, 50, 50)

    assert panel._last_mouse_position is not None
    assert panel._click_press_position is not None
