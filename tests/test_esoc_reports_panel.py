"""
Tests for acf.gui.esoc.panel_manager.ReportsPanel - the real Executive
Risk Briefings / Climate Impact Assessments panel closing the
previously-empty "Reports" System Explorer category (2026-09-04,
seventh and last of 7 ESOC categories with no real panel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import ReportsPanel
from acf.intelligence.reports.executive_report import AutonomousReportGenerator


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_executive_report_shows_the_real_honest_disclosure(qapp, registry):
    dispatcher = CommandDispatcher()

    panel = ReportsPanel(registry, dispatcher)

    expected = AutonomousReportGenerator.generate_executive_intelligence_report()
    assert expected["is_real_data"] == "False"
    assert panel.executive_report_result == expected
    assert "NOT GENERATED" in expected["content"]


def test_climate_horizon_computed_on_construction_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()

    panel = ReportsPanel(registry, dispatcher)

    expected = registry.get_module("ssp_engine").evaluate_horizon(int(panel.climate_year.currentText()))
    text = panel.climate_result.toPlainText()
    assert expected["scenario"] in text
    assert f"{expected['global_temp_anomaly_c']:.2f}" in text
    assert f"{expected['sea_level_rise_m']:.3f}" in text


def test_climate_horizon_genuinely_varies_with_the_real_target_year(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ReportsPanel(registry, dispatcher)

    panel.climate_year.setCurrentText("2030")
    panel.climate_button.click()
    near_term = panel.climate_result.toPlainText()

    panel.climate_year.setCurrentText("2300")
    panel.climate_button.click()
    far_term = panel.climate_result.toPlainText()

    assert near_term != far_term
    expected_2030 = registry.get_module("ssp_engine").evaluate_horizon(2030)
    expected_2300 = registry.get_module("ssp_engine").evaluate_horizon(2300)
    assert expected_2300["global_temp_anomaly_c"] > expected_2030["global_temp_anomaly_c"]


def test_reports_panel_honestly_discloses_when_ssp_engine_is_not_connected(qapp, tmp_path):
    class _EmptyRegistry:
        def get_module(self, name: str):
            return None

    dispatcher = CommandDispatcher()
    panel = ReportsPanel(_EmptyRegistry(), dispatcher)  # type: ignore[arg-type]

    assert not hasattr(panel, "climate_button")
