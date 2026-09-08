"""
Tests for acf.gui.esoc.panel_manager.BiospherePanel - the real dynamic
vegetation model panel closing the previously-dead "Earth System /
Biosphere" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import BiospherePanel
from acf.simulation_engine.land_solver.vegetation_model import VegetationModel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = BiospherePanel(registry, dispatcher)
    panel.temp_c.setValue(25.0)
    panel.soil_moisture.setValue(0.3)
    panel.solar.setValue(600.0)

    panel.button.click()

    expected = VegetationModel().compute_vegetation_indices(
        temperature_k=np.array([[298.15]]), soil_moisture=np.array([[0.3]]), solar_radiation=np.array([[600.0]])
    )
    text = panel.result.toPlainText()
    assert f"{float(expected['LAI'][0, 0]):.3f}" in text
    assert f"{float(expected['NDVI'][0, 0]):.3f}" in text
    assert f"{float(expected['NPP'][0, 0]):.3f}" in text


def test_freezing_temperature_genuinely_halts_real_growth(qapp, registry):
    """Real physical sanity: VegetationModel's own temperature-growth
    factor clips to 0 far outside its real optimal range - a genuinely
    responsive real formula, not a fixed placeholder."""
    dispatcher = CommandDispatcher()
    panel = BiospherePanel(registry, dispatcher)
    panel.temp_c.setValue(-20.0)

    panel.button.click()

    assert "Real LAI: 0.000" in panel.result.toPlainText()


def test_warm_moist_sunlit_input_produces_real_non_zero_growth(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = BiospherePanel(registry, dispatcher)
    panel.temp_c.setValue(25.0)
    panel.soil_moisture.setValue(0.3)
    panel.solar.setValue(800.0)

    panel.button.click()

    text = panel.result.toPlainText()
    assert "Real LAI: 0.000" not in text


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["vegetation_model"] = None

    panel = BiospherePanel(registry, dispatcher)

    assert not hasattr(panel, "button")
