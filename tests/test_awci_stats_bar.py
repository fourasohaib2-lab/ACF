"""
Tests for acf.gui.dashboard.awci_stats_bar - specifically the real
half-circle FORECAST CONFIDENCE gauge (docs/reference/
awci_dashboard_reference.jpg parity work, added 2026-09-03: replaces
the plain-text confidence stat box with a real AWCIGauge(half_circle=True),
fed by the exact same real confidence_pct value).
"""

from __future__ import annotations

from acf.gui.dashboard.awci_gauge import AWCIGauge
from acf.gui.dashboard.awci_stats_bar import AWCIStatsBar


def test_confidence_box_hosts_a_real_half_circle_gauge(qtbot):
    bar = AWCIStatsBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.confidence_box.gauge, AWCIGauge)
    assert bar.confidence_box.gauge._half_circle is True


def test_update_data_sets_the_real_gauge_score(qtbot):
    bar = AWCIStatsBar()
    qtbot.addWidget(bar)

    bar.update_data([10.0, 50.0, 90.0], confidence_pct=72.0)

    assert bar.confidence_box.gauge._score == 72.0


def test_default_confidence_matches_the_documented_default(qtbot):
    bar = AWCIStatsBar()
    qtbot.addWidget(bar)

    bar.update_data([10.0, 50.0, 90.0])  # confidence_pct defaults to 75.0

    assert bar.confidence_box.gauge._score == 75.0


def test_other_stat_boxes_are_unaffected_by_the_gauge_change(qtbot):
    """Bit-identical behavior for the other 4 boxes."""
    bar = AWCIStatsBar()
    qtbot.addWidget(bar)

    bar.update_data([10.0, 50.0, 90.0, 70.0], confidence_pct=72.0)

    assert bar.mean_box.value_lbl.text() == "55"
    assert bar.max_box.value_lbl.text() == "90"
    assert bar.area_box.value_lbl.text() == "50.0%"


def test_model_box_still_plain_text(qtbot):
    bar = AWCIStatsBar()
    qtbot.addWidget(bar)
    assert bar.model_box.value_lbl.text() == "ACF Demo Grid"
