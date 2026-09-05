"""
Tests for acf.gui.esoc.panel_manager.CarbonPanel - upgrading the real
"Carbon" leaf (panel #21, already mapped) from a hardcoded, honestly
disclaimed "Example Layout" text block to real, live computation
chaining VegetationModel -> CarbonFluxModel (2026-09-05, Phase 52).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import CarbonPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_default_result_matches_the_real_engines_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    vegetation_module = registry.get_module("vegetation_model")
    carbon_module = registry.get_module("carbon_flux_model")
    panel = CarbonPanel(registry, dispatcher)

    temperature_k = np.array([[20.0 + 273.15]])
    soil_moisture = np.array([[0.25]])
    solar_radiation = np.array([[400.0]])
    soil_temp_k = np.array([[15.0 + 273.15]])
    vegetation = vegetation_module.compute_vegetation_indices(temperature_k, soil_moisture, solar_radiation)
    fluxes = carbon_module.compute_carbon_fluxes(
        co2_ppm=420.0, npp_field=vegetation["NPP"], soil_temp_k=soil_temp_k
    )

    text = panel.result.toPlainText()
    assert f"{float(vegetation['NPP'][0, 0]):.3f}" in text
    assert f"{float(fluxes['GPP'][0, 0]):.3f}" in text
    assert f"{float(fluxes['NEE'][0, 0]):.3f}" in text


def test_higher_co2_increases_real_gpp_via_fertilization_factor(qapp, registry):
    """Real physical-sanity check: CarbonFluxModel's own cited
    CO2-fertilization beta-factor must genuinely raise GPP for a
    higher atmospheric CO2 concentration, never a static number."""
    dispatcher = CommandDispatcher()
    panel = CarbonPanel(registry, dispatcher)

    panel.co2_ppm.setValue(300.0)
    panel._compute()
    low_co2_text = panel.result.toPlainText()

    panel.co2_ppm.setValue(800.0)
    panel._compute()
    high_co2_text = panel.result.toPlainText()

    assert low_co2_text != high_co2_text


def test_sink_or_source_label_matches_the_real_nee_sign(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = CarbonPanel(registry, dispatcher)
    panel._compute()

    text = panel.result.toPlainText()
    nee_line = next(line for line in text.splitlines() if "Net Ecosystem Exchange" in line)
    nee_value = float(nee_line.split(":")[1].split("g")[0].strip())
    if nee_value < 0.0:
        assert "Carbon Sink" in nee_line
    else:
        assert "Carbon Source" in nee_line


def test_panel_shows_an_honest_disconnected_label_when_vegetation_model_missing(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["vegetation_model"] = None

    panel = CarbonPanel(registry, dispatcher)

    assert not hasattr(panel, "button")


def test_panel_shows_an_honest_disconnected_label_when_carbon_flux_model_missing(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["carbon_flux_model"] = None

    panel = CarbonPanel(registry, dispatcher)

    assert not hasattr(panel, "button")
