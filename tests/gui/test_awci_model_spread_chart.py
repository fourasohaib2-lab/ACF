"""
Tests for AWCIModelSpreadChart (src/acf/gui/dashboard/awci_model_spread_chart.py) -
explicit user request "vasy respecte le prompt", matching the general ACF
dashboard reference mockup's "MULTI-MODEL CONSENSUS SPREAD" panel. Fed
from real acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine.compute_real_multi_model_disagreement() output shapes.
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_model_spread_chart import AWCIModelSpreadChart


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_empty_with_honest_placeholder(qapp):
    chart = AWCIModelSpreadChart()
    assert chart.status() == {"figure": True, "axis": True}
    texts = [t.get_text() for t in chart.axis.texts]
    assert any("not yet computed" in t.lower() for t in texts)


def test_set_data_draws_one_bar_per_real_model(qapp):
    chart = AWCIModelSpreadChart()
    per_model_value = {"ARPEGE": 290.1, "ALADIN": 291.4}
    chart.set_data(per_model_value, disagreement_mean=290.75, disagreement_spread=0.9, variable_label="Temperature (K)")

    bars = chart.axis.patches
    assert len(bars) == len(per_model_value)
    heights = sorted(bar.get_height() for bar in bars)
    assert heights == sorted(per_model_value.values())


def test_set_data_clears_the_empty_placeholder_text(qapp):
    chart = AWCIModelSpreadChart()
    chart.set_data({"ARPEGE": 290.0, "ALADIN": 291.0}, disagreement_mean=290.5, disagreement_spread=0.5, variable_label="Temperature (K)")
    texts = [t.get_text() for t in chart.axis.texts]
    assert not any("not yet computed" in t.lower() for t in texts)


def test_set_data_draws_a_real_mean_line(qapp):
    chart = AWCIModelSpreadChart()
    chart.set_data({"ARPEGE": 290.0, "ALADIN": 291.0}, disagreement_mean=290.5, disagreement_spread=0.5, variable_label="Temperature (K)")
    lines = chart.axis.get_lines()
    assert len(lines) == 1
    ys = lines[0].get_ydata()
    assert all(y == 290.5 for y in ys)


def test_model_outside_the_spread_band_is_colored_differently_than_one_inside(qapp):
    chart = AWCIModelSpreadChart()
    # ARPEGE inside [mean - spread, mean + spread], ALADIN far outside.
    chart.set_data({"ARPEGE": 290.0, "ALADIN": 310.0}, disagreement_mean=290.0, disagreement_spread=0.5, variable_label="Temperature (K)")
    bars = chart.axis.patches
    colors = {bar.get_height(): bar.get_facecolor() for bar in bars}
    assert colors[290.0] != colors[310.0]
