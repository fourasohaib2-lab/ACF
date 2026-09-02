"""
Tests for AWCIRiskSummary (src/acf/gui/dashboard/awci_risk_summary.py).

Covers the Physical/Forecast Complexity rows added 2026-09-02 alongside
AWCICalculator.calculate()'s physical_score/forecast_score split (see
that module's docstring and docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's
Complexity Engine section for the full rationale).
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_risk_summary import AWCIRiskSummary


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_risk_summary_has_physical_and_forecast_rows(qapp):
    panel = AWCIRiskSummary()
    assert "physical" in panel._rows
    assert "forecast" in panel._rows


def test_risk_summary_shows_real_physical_and_forecast_levels(qapp):
    panel = AWCIRiskSummary()
    module_scores = {"dynamic": 40.0, "microphysical": 20.0, "convective": 90.0}

    panel.update_data(module_scores, overall_awci=55.0, physical_score=76.0, forecast_score=91.0)

    physical_badge = panel._rows["physical"][1]
    forecast_badge = panel._rows["forecast"][1]
    assert physical_badge.text() != "—"
    assert forecast_badge.text() != "—"


def test_risk_summary_shows_dash_not_a_fabricated_score_when_undefined(qapp):
    """
    CORRECTED principle applied here: physical_score/forecast_score can
    legitimately be None (AWCICalculator._renormalized_score() returns
    None when a whole dimension's weight budget is ~0). The panel must
    show "—", never silently default to 0.0 - which would read as "no
    complexity", a fabricated result indistinguishable from a genuinely
    calm atmosphere.
    """
    panel = AWCIRiskSummary()
    panel.update_data({}, overall_awci=10.0, physical_score=None, forecast_score=None)

    physical_badge = panel._rows["physical"][1]
    forecast_badge = panel._rows["forecast"][1]
    assert physical_badge.text() == "—"
    assert forecast_badge.text() == "—"


def test_risk_summary_defaults_to_dash_when_scores_not_supplied(qapp):
    """Backward-compat call (no physical_score/forecast_score kwargs) must not crash."""
    panel = AWCIRiskSummary()
    panel.update_data({"dynamic": 30.0}, overall_awci=25.0)

    assert panel._rows["physical"][1].text() == "—"
    assert panel._rows["forecast"][1].text() == "—"
    assert panel._rows["overall"][1].text() != "—"
