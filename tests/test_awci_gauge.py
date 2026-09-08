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
