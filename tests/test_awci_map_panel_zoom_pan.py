"""
Tests for acf.gui.dashboard.awci_map_panel.AWCIMapPanel's real
interactive zoom/pan (explicit user request "ajoute l'option zoom des
cartes et manipulation totale des cartes"), reusing the same
EventMixin + MapCamera wiring (and event-filter-on-the-child-canvas
lesson) as acf.gui.map.map_canvas.MapCanvas - see
tests/test_map_canvas_zoom_pan.py's own docstring for why events are
dispatched to `panel.canvas` (the real target of Qt's input delivery),
not to AWCIMapPanel's own handler methods directly.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel

_REGIONAL_EXTENT = (-12.0, 35.0, 15.0, 40.0)


def _send_wheel(panel: AWCIMapPanel, delta_y: int) -> None:
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
    assert QApplication.sendEvent(panel.canvas, event)


def test_real_scroll_over_the_global_panel_genuinely_zooms_in(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    before = panel.camera.current_extent()
    _send_wheel(panel, 120)
    after = panel.camera.current_extent()
    assert (after[1] - after[0]) < (before[1] - before[0])


def test_regional_panel_starts_at_its_own_configured_extent_not_the_world():
    panel = AWCIMapPanel("AWCI REGIONAL MAP", extent=_REGIONAL_EXTENT)
    extent = panel.camera.current_extent()
    assert extent[0] == pytest.approx(_REGIONAL_EXTENT[0])
    assert extent[1] == pytest.approx(_REGIONAL_EXTENT[1])


def test_zoom_survives_a_real_data_refresh_update_data_call(qtbot):
    """Real regression guard: update_data() used to call
    axis.set_extent()/set_global() unconditionally on every redraw
    (including every time_slider move in AWCIDashboard), which would
    have silently thrown away any zoom/pan the user had made."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    _send_wheel(panel, 120)
    zoomed = panel.camera.current_extent()
    panel.update_data(flight_level_hpa=700.0, time_offset_hours=5.0)  # simulates AWCIDashboard's time_slider handler
    assert panel.camera.current_extent() == pytest.approx(zoomed)


def test_reset_view_returns_to_the_panels_own_extent_not_the_world(qtbot):
    panel = AWCIMapPanel("AWCI REGIONAL MAP", extent=_REGIONAL_EXTENT)
    qtbot.addWidget(panel)
    _send_wheel(panel, 120)
    assert panel.camera.current_extent() != pytest.approx(
        [_REGIONAL_EXTENT[0], _REGIONAL_EXTENT[1], _REGIONAL_EXTENT[2], _REGIONAL_EXTENT[3]]
    )
    panel.reset_view()
    extent = panel.camera.current_extent()
    assert extent[0] == pytest.approx(_REGIONAL_EXTENT[0])
    assert extent[1] == pytest.approx(_REGIONAL_EXTENT[1])


def test_global_panel_reset_view_returns_to_the_whole_world(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    _send_wheel(panel, 120)
    panel.reset_view()
    assert panel.camera.current_extent() == pytest.approx([-180.0, 180.0, -90.0, 90.0])


def test_on_canvas_zoom_buttons_are_real_and_wired(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    before = panel.camera.current_extent()
    qtbot.mouseClick(panel.zoom_in_button, Qt.MouseButton.LeftButton)
    after = panel.camera.current_extent()
    assert (after[1] - after[0]) < (before[1] - before[0])
