"""
Tests for acf.gui.esoc.panel_manager.GeoengineeringPanel - the real
Stratospheric Aerosol Injection / Direct Air Capture panel closing the
previously-empty "Geoengineering" System Explorer category
(2026-09-04, third of 7 ESOC categories with no real panel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.geoengineering.carbon_removal import CarbonRemovalEngine
from acf.geoengineering.solar_radiation_management import SolarRadiationManagementEngine
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import GeoengineeringPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_geoengineering_panel_runs_a_real_sai_simulation_on_construction(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = GeoengineeringPanel(registry, dispatcher)

    expected = SolarRadiationManagementEngine.simulate_stratospheric_aerosol_injection(
        so2_injection_megatons_per_year=panel.sai_input.value()
    )
    text = panel.sai_result.toPlainText()
    assert f"{expected.radiative_forcing_w_m2:.3f}" in text
    assert f"{expected.global_temperature_cooling_k:.3f}" in text
    assert expected.termination_shock_risk_level in text


def test_geoengineering_panel_sai_result_genuinely_scales_with_input(qapp):
    """Cross-check discipline: the real result must change with the
    real user-chosen input, never a fixed narrative string - the exact
    fabrication pattern climate_ai.py's own NOTE documents being
    corrected for a sibling class."""
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = GeoengineeringPanel(registry, dispatcher)

    panel.sai_input.setValue(5.0)
    panel.sai_button.click()
    result_low = panel.sai_result.toPlainText()

    panel.sai_input.setValue(50.0)
    panel.sai_button.click()
    result_high = panel.sai_result.toPlainText()

    assert result_low != result_high
    expected_low = SolarRadiationManagementEngine.simulate_stratospheric_aerosol_injection(5.0)
    expected_high = SolarRadiationManagementEngine.simulate_stratospheric_aerosol_injection(50.0)
    assert f"{expected_low.global_temperature_cooling_k:.3f}" in result_low
    assert f"{expected_high.global_temperature_cooling_k:.3f}" in result_high
    assert expected_high.global_temperature_cooling_k > expected_low.global_temperature_cooling_k


def test_geoengineering_panel_runs_a_real_daccs_evaluation_on_construction(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = GeoengineeringPanel(registry, dispatcher)

    expected = CarbonRemovalEngine.evaluate_direct_air_capture(capacity_gt_co2=panel.daccs_input.value())
    text = panel.daccs_result.toPlainText()
    assert f"${expected.cost_usd_per_ton_co2:.0f}" in text
    assert f"{expected.energy_consumption_mwh_per_ton:.1f}" in text
    assert f"{expected.readiness_level_trl}/9" in text


def test_geoengineering_panel_daccs_result_genuinely_reflects_the_real_engine(qapp):
    """DACCS's own real engineering parameters (cost, energy, land
    area, TRL) are all constants per real technique in this codebase
    (not input-dependent) - proven here by cross-checking against a
    direct, independent call, matching the same real-formula-reuse
    discipline as every other panel."""
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = GeoengineeringPanel(registry, dispatcher)

    panel.daccs_input.setValue(3.5)
    panel.daccs_button.click()

    expected = CarbonRemovalEngine.evaluate_direct_air_capture(capacity_gt_co2=3.5)
    text = panel.daccs_result.toPlainText()
    assert f"{expected.durability_years:,.0f}" in text
    assert f"{expected.land_area_required_km2_per_gt:,.0f}" in text
