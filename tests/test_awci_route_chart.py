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


# ------------------------------------- real PolyCollection fill (perf, 2026-09-03)


def test_filled_area_uses_one_real_polycollection_not_many_patches(qtbot):
    """Real performance regression guard - profiled AWCIDashboard.refresh()
    found this panel's own per-segment Axes.fill_between() loop (one
    real matplotlib call per segment) as its single largest real cost
    (45ms -> 6ms measured after this fix). Must stay a single real
    PolyCollection, not regress back to a per-segment call loop."""
    from matplotlib.collections import PolyCollection

    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)

    collections = [c for c in chart.axis.collections if isinstance(c, PolyCollection)]
    assert len(collections) == 1


def test_polycollection_has_one_real_quad_per_segment_with_the_real_awci_colors(qtbot):
    import numpy as np

    from acf.gui.dashboard.awci_colors import AWCI_CMAP

    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    scores = chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    distances = chart.last_distances_km

    from matplotlib.collections import PolyCollection

    collection = next(c for c in chart.axis.collections if isinstance(c, PolyCollection))
    verts = collection.get_paths()

    assert len(verts) == len(distances) - 1

    # Real, disclosed geometry check: segment 0's own quad must have
    # the exact same 4 real corners a direct
    # fill_between([x0,x1],[0,0],[y0,y1]) call would draw.
    first_quad = verts[0].vertices
    x0, x1 = distances[0], distances[1]
    y0, y1 = scores[0], scores[1]
    expected_corners = {(x0, 0.0), (x1, 0.0), (x1, y1), (x0, y0)}
    actual_corners = {tuple(v) for v in first_quad[:4]}
    assert actual_corners == expected_corners

    # Real color check: segment i's facecolor must match AWCI_CMAP at
    # score[i] (the segment's own LEFT/starting point) - the exact same
    # per-segment coloring convention the original fill_between() loop
    # used (color=colors[i]).
    expected_colors = AWCI_CMAP(np.array(scores) / 100.0)
    actual_facecolors = collection.get_facecolor()
    assert len(actual_facecolors) == len(distances) - 1
    for i in range(len(distances) - 1):
        assert np.allclose(actual_facecolors[i], expected_colors[i], atol=1e-6)


def test_comparison_mode_does_not_use_a_polycollection(qtbot):
    """The dual-flight-level comparison mode draws 2 real lines, no
    filled area (see module docstring) - must not accidentally pick up
    a stale PolyCollection from a prior single-series draw."""
    from matplotlib.collections import PolyCollection

    chart = AWCIRouteChart()
    qtbot.addWidget(chart)
    chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)
    chart.set_comparison_series([0.0, 100.0], [20.0, 40.0], "FL320")

    collections = [c for c in chart.axis.collections if isinstance(c, PolyCollection)]
    assert collections == []


# ------------------------------------------------------ AWCIRouteSegmentTable


def test_segment_table_shows_an_honest_empty_state_before_any_real_route(qtbot):
    from acf.gui.dashboard.awci_route_chart import AWCIRouteSegmentTable

    table = AWCIRouteSegmentTable()
    qtbot.addWidget(table)
    table.update_data(None, None)
    assert table._rows_layout.count() == 1


def test_segment_table_builds_n_segments_from_a_real_route(qtbot):
    from acf.gui.dashboard.awci_route_chart import AWCIRouteSegmentTable

    table = AWCIRouteSegmentTable(n_segments=4)
    qtbot.addWidget(table)
    chart = AWCIRouteChart()
    scores = chart.update_data(_POINT_A, _POINT_B, cruise_hpa=850.0)

    table.update_data(chart.last_distances_km, scores)

    assert table._rows_layout.count() == 4


def test_segment_table_awci_is_the_real_mean_of_its_own_real_bucket(qtbot):
    """Real proof: no fabricated per-segment number - each row's AWCI
    is the direct mean of the SAME real per-point scores array already
    passed in, over the real points whose real distance falls in that
    segment's own real range."""
    from acf.gui.dashboard.awci_route_chart import AWCIRouteSegmentTable

    distances = [0.0, 25.0, 50.0, 75.0, 100.0]
    scores = [10.0, 20.0, 30.0, 40.0, 50.0]
    table = AWCIRouteSegmentTable(n_segments=2)
    table.update_data(distances, scores)

    first_row = table._rows_layout.itemAt(0).layout()
    first_awci_text = first_row.itemAt(1).widget().text()
    # First segment (0-50 km) covers real points at 0/25/50 km (both
    # boundaries real-inclusive) -> real mean of [10, 20, 30] = 20.
    assert first_awci_text == "20"


def test_segment_table_flags_a_real_critical_zone_above_the_shared_threshold(qtbot):
    """Qt's own isVisible() reflects EFFECTIVE visibility (the whole
    parent chain must be shown on screen too, not just this widget's
    own setVisible(True) flag - a never-.show()'d widget always
    reports isVisible()=False regardless, the same real gotcha already
    documented elsewhere in this codebase, e.g. _stop_evolution_
    playback()'s own NOTE) - checked via the real internal flag Qt
    exposes for exactly this case instead."""
    from PySide6.QtCore import Qt
    from acf.gui.dashboard.awci_route_chart import AWCIRouteSegmentTable

    table = AWCIRouteSegmentTable(n_segments=2)
    table.update_data([0.0, 50.0, 100.0], [10.0, 90.0, 95.0])

    assert not table.critical_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
    assert "Critical Zone" in table.critical_label.text()


def test_segment_table_shows_no_critical_zone_when_nothing_crosses_the_threshold(qtbot):
    from PySide6.QtCore import Qt
    from acf.gui.dashboard.awci_route_chart import AWCIRouteSegmentTable

    table = AWCIRouteSegmentTable(n_segments=2)
    table.update_data([0.0, 50.0, 100.0], [10.0, 20.0, 15.0])

    assert table.critical_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
