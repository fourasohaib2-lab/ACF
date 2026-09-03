"""
Tests for AWCIEvolutionChart (src/acf/gui/dashboard/awci_evolution_chart.py) -
explicit user request "vasy respecte le prompt", matching the general ACF
dashboard reference mockup's "AWCI EVOLUTION (24h)" panel.
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_evolution_chart import AWCIEvolutionChart


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_empty_with_honest_placeholder(qapp):
    chart = AWCIEvolutionChart()
    assert chart.status() == {"figure": True, "axis": True}
    texts = [t.get_text() for t in chart.axis.texts]
    assert any("no real evolution" in t.lower() for t in texts)


def test_set_series_draws_a_real_line_with_the_supplied_values(qapp):
    chart = AWCIEvolutionChart()
    valid_time_hours = [0.0, 3.0, 6.0, 12.0, 24.0]
    awci_mean = [10.0, 15.0, 20.0, 25.0, 18.0]
    awci_max = [20.0, 28.0, 35.0, 40.0, 30.0]

    chart.set_series(valid_time_hours, awci_mean, awci_max, current_frame_index=2)

    lines = chart.axis.get_lines()
    # Mean line + max line (+ one axvline for the current-frame marker)
    assert len(lines) >= 2
    import numpy as np

    xs, ys = lines[0].get_xdata(), lines[0].get_ydata()
    np.testing.assert_allclose(xs, valid_time_hours)
    np.testing.assert_allclose(ys, awci_mean)


def test_set_series_clears_the_empty_placeholder_text(qapp):
    chart = AWCIEvolutionChart()
    chart.set_series([0.0, 1.0], [10.0, 12.0], [15.0, 18.0])
    texts = [t.get_text() for t in chart.axis.texts]
    assert not any("no real evolution" in t.lower() for t in texts)


def test_set_series_without_current_frame_index_still_draws(qapp):
    chart = AWCIEvolutionChart()
    chart.set_series([0.0, 6.0], [5.0, 9.0], [8.0, 14.0], current_frame_index=None)
    assert len(chart.axis.get_lines()) >= 2


def test_y_axis_is_fixed_to_the_real_awci_0_100_range(qapp):
    chart = AWCIEvolutionChart()
    chart.set_series([0.0, 6.0], [5.0, 9.0], [8.0, 14.0])
    assert chart.axis.get_ylim() == (0.0, 100.0)
