"""
Tests for acf.gui.dashboard.awci_gauge.AWCIGauge - specifically the
real half-circle mode (docs/reference/awci_dashboard_reference.jpg
parity work, added 2026-09-03: the mockup's "FORECAST CONFIDENCE"
gauge is a half-circle band, reusing this widget's own real arc-
drawing/needle code rather than a second widget - see module
docstring's "Half-circle mode" note). This widget was previously dead
code (not instantiated by anything) - first real, live test coverage.
"""

from __future__ import annotations

from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_gauge import AWCIGauge


def test_default_constructor_is_full_circle(qtbot):
    gauge = AWCIGauge()
    qtbot.addWidget(gauge)
    assert gauge._half_circle is False
    assert gauge._start_angle == 135
    assert gauge._span_angle == 270


def test_half_circle_constructor_uses_a_180_degree_arc(qtbot):
    gauge = AWCIGauge(half_circle=True)
    qtbot.addWidget(gauge)
    assert gauge._half_circle is True
    assert gauge._start_angle == 180
    assert gauge._span_angle == 180


def test_half_circle_has_a_shorter_minimum_height_than_full_circle(qtbot):
    full = AWCIGauge(half_circle=False)
    half = AWCIGauge(half_circle=True)
    qtbot.addWidget(full)
    qtbot.addWidget(half)
    assert half.minimumSize().height() < full.minimumSize().height()
    assert half.minimumSize().width() == full.minimumSize().width()


def test_set_score_clamps_to_0_100_in_both_modes(qtbot):
    for gauge in (AWCIGauge(), AWCIGauge(half_circle=True)):
        qtbot.addWidget(gauge)
        gauge.set_score(150.0, animate=False)
        assert gauge._score == 100.0
        gauge.set_score(-10.0, animate=False)
        assert gauge._score == 0.0


def test_set_score_without_animation_is_immediate(qtbot):
    gauge = AWCIGauge(half_circle=True)
    qtbot.addWidget(gauge)
    gauge.set_score(72.0, animate=False)
    assert gauge._score == 72.0
    assert gauge._target_score == 72.0


def test_get_level_and_color_matches_the_real_awci_bands(qtbot):
    gauge = AWCIGauge(half_circle=True)
    qtbot.addWidget(gauge)
    level, _color = gauge._get_level_and_color(72.0)
    assert level == "Very High"  # 65 <= 72 < 85
    level_low, _ = gauge._get_level_and_color(5.0)
    assert level_low == "Very Low"


def test_paint_event_does_not_raise_for_half_circle(qtbot):
    """Real regression guard: the half-circle geometry (bottom-pivot
    center, constrained arc_rect) must not crash the real paintEvent."""
    gauge = AWCIGauge(half_circle=True)
    qtbot.addWidget(gauge)
    gauge.resize(220, 130)
    gauge.set_score(72.0, animate=False)
    gauge.show()  # triggers a real paintEvent - must not raise


def test_paint_event_does_not_raise_for_full_circle(qtbot):
    gauge = AWCIGauge(half_circle=False)
    qtbot.addWidget(gauge)
    gauge.resize(200, 200)
    gauge.set_score(35.0, animate=False)
    gauge.show()  # must not raise


def test_half_circle_score_and_level_text_boxes_do_not_overlap(qtbot, monkeypatch):
    """Real regression guard for the /verify runtime-drive finding
    (2026-09-12): 2 real screenshots of the live FORECAST CONFIDENCE
    gauge showed "100"/"Extreme" superposed - `level_text_y` was only
    +30 past `score_text_y` while the score text box above it is 40px
    tall. Drives the real paintEvent and spies on the real QPainter.
    drawText(x, y, w, h, flags, text) calls it makes, so this fails
    again if the same 10px shortfall (or any new overlap) regresses."""
    calls: list[tuple[int, int, int, int]] = []
    original_draw_text = QPainter.drawText

    def spy_draw_text(self, *args):
        if len(args) >= 4 and isinstance(args[0], int) and isinstance(args[1], int):
            calls.append((args[0], args[1], args[2], args[3]))
        return original_draw_text(self, *args)

    monkeypatch.setattr(QPainter, "drawText", spy_draw_text)

    gauge = AWCIGauge(half_circle=True)
    qtbot.addWidget(gauge)
    gauge.resize(220, 130)
    gauge.set_score(100.0, animate=False)
    gauge.show()
    QApplication.instance().processEvents()

    assert len(calls) == 2, "expected exactly 2 int-rect drawText calls: the score text, then the level text"
    (_score_x, score_y, _score_w, score_h), (_level_x, level_y, _level_w, _level_h) = calls
    score_box_bottom = score_y + score_h
    assert level_y >= score_box_bottom, (
        f"level text (y={level_y}) must start at or after the score text box's own bottom "
        f"(y={score_box_bottom}) - a smaller level_y means the two texts visually overlap"
    )
