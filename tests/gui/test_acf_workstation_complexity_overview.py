from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_complexity_overview import ComplexityOverviewPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_gauge_is_the_disclosed_mean_of_real_factors(qapp, qtbot):
    panel = ComplexityOverviewPanel()
    qtbot.addWidget(panel)
    factors = {
        "Instability": 0.82, "Moisture": 0.76, "Shear": 0.68, "Convection": 0.71,
        "Gradients": 0.64, "Vertical Structure": 0.72, "Temporal Evolution": 0.69,
        "Model Disagreement": 0.58,
    }
    panel.update_from_factors(factors)
    expected_mean = sum(factors.values()) / len(factors)
    assert panel.composite_score == pytest.approx(expected_mean)
    assert f"{expected_mean:.2f}" in panel.gauge_label.text()


def test_gauge_ignores_missing_factors_in_the_mean(qapp, qtbot):
    panel = ComplexityOverviewPanel()
    qtbot.addWidget(panel)
    factors = {"Instability": 0.8, "Moisture": None, "Shear": 0.4}
    panel.update_from_factors(factors)
    assert panel.composite_score == pytest.approx((0.8 + 0.4) / 2)


def test_gauge_with_no_real_factors_is_honest(qapp, qtbot):
    panel = ComplexityOverviewPanel()
    qtbot.addWidget(panel)
    panel.update_from_factors({"Instability": None})
    assert panel.composite_score is None
    assert "NOT_COMPUTED" in panel.gauge_label.text()
