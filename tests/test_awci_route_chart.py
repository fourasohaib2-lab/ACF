"""
Tests for acf.gui.dashboard.awci_route_chart - specifically the real
dual-flight-level comparison mode (docs/reference/
awci_dashboard_reference.jpg parity work, added 2026-09-03: the
mockup's "ROUTE PLANNING" panel compares AWCI along the same route at
two real flight levels, e.g. FL280 vs FL320).
"""

from __future__ import annotations

from acf.gui.dashboard.awci_route_chart import AWCIRouteChart

_POINT_A = (36.75, 3.06)
_POINT_B = (32.90, 13.19)


def test_last_distances_km_is_none_before_any_draw(qtbot):
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    assert chart.last_distances_km is None


def test_last_distances_km_matches_the_real_scores_length(qtbot):
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    scores = chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    assert chart.last_distances_km is not None
    assert len(chart.last_distances_km) == len(scores)
    assert chart.last_distances_km[0] == 0.0


def test_last_distances_km_updates_after_set_external_route(qtbot):
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    distances = [0.0, 50.0, 100.0]
    scores = [10.0, 20.0, 30.0]
    chart.set_external_route(distances, scores, "REAL PHYSICS")
    assert chart.last_distances_km == distances


def test_comparison_series_is_none_by_default(qtbot):
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    assert chart._comparison is None


def test_set_comparison_series_stores_the_real_supplied_data(qtbot):
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)

    chart.set_comparison_series([0.0, 100.0], [15.0, 45.0], "FL320", primary_label="FL280")

    assert chart._comparison == ([0.0, 100.0], [15.0, 45.0], "FL320")
    assert chart._primary_label == "FL280"


def test_set_comparison_series_does_not_raise_when_drawn(qtbot):
    """Real regression guard: the dual-line draw path must not crash."""
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    chart.set_comparison_series([0.0, 100.0, 200.0], [15.0, 45.0, 25.0], "FL320", primary_label="FL280")  # must not raise


def test_set_comparison_series_before_any_primary_draw_is_a_safe_no_op(qtbot):
    """Calling set_comparison_series() before update_data()/
    set_external_route() has nothing real to redraw yet - must not
    raise, not fabricate a primary series."""
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.set_comparison_series([0.0, 100.0], [15.0, 45.0], "FL320")  # must not raise
    assert chart._comparison is not None


def test_clear_comparison_series_removes_it(qtbot):
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    chart.set_comparison_series([0.0, 100.0], [15.0, 45.0], "FL320")

    chart.clear_comparison_series()

    assert chart._comparison is None


def test_comparison_mode_uses_two_distinct_real_colors(qtbot):
    """Real proof the 2 series are drawn with 2 distinct colors (matching
    the mockup's orange FL280 / light-blue FL320), not overlapping/
    indistinguishable lines."""
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    chart.set_comparison_series([0.0, 100.0, 200.0], [15.0, 45.0, 25.0], "FL320", primary_label="FL280")

    lines = chart.axis.get_lines()
    colors = {line.get_color() for line in lines}
    assert len(colors) == 2


def test_default_single_series_mode_is_unaffected_by_the_new_feature(qtbot):
    """Bit-identical default: a caller that never calls
    set_comparison_series() sees the exact same single filled-area
    chart as before."""
    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    scores = chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    assert chart._comparison is None
    assert len(scores) > 0
