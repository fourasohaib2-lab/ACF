"""
Tests for acf.gui.esoc.panel_manager.LandSurfacePanel - the real
4-layer soil model panel closing the previously-dead "Earth System /
Land Surface" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import LandSurfacePanel
from acf.simulation_engine.land_solver.soil_model import SoilModel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_starts_with_the_real_default_initial_soil_state(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = LandSurfacePanel(registry, dispatcher)

    assert panel.table.item(0, 1).text() == "0.2500"
    assert panel.table.item(0, 2).text() == "288.15"


def test_advance_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = LandSurfacePanel(registry, dispatcher)
    panel.precip.setValue(15.0)
    panel.evapo.setValue(0.5)
    panel.surface_temp.setValue(300.0)
    panel.dt_hours.setValue(2.0)

    panel.button.click()

    expected_state = SoilModel().initialize_soil_state((1, 1))
    to_m_s = 1.0 / (1000.0 * 3600.0)
    expected_state = SoilModel().step(
        expected_state,
        precip_rate=np.full((1, 1), 15.0 * to_m_s),
        evapotranspiration=np.full((1, 1), 0.5 * to_m_s),
        surface_temp=np.full((1, 1), 300.0),
        dt=2.0 * 3600.0,
    )
    assert panel.table.item(0, 1).text() == f"{float(expected_state['soil_moisture'][0, 0, 0]):.4f}"
    assert panel.table.item(0, 2).text() == f"{float(expected_state['soil_temperature'][0, 0, 0]):.2f}"


def test_heavy_rain_saturates_the_real_surface_layer(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = LandSurfacePanel(registry, dispatcher)
    panel.precip.setValue(200.0)
    panel.dt_hours.setValue(24.0)

    panel.button.click()

    assert panel.table.item(0, 1).text() == "0.4500"  # real porosity bound


def test_deeper_layers_are_genuinely_unaffected_by_one_real_step(qapp, registry):
    """Real regression guard matching this model's own documented
    scope: only the surface layer (layer 0) updates per real step."""
    dispatcher = CommandDispatcher()
    panel = LandSurfacePanel(registry, dispatcher)
    panel.precip.setValue(50.0)

    panel.button.click()

    for layer in (1, 2, 3):
        assert panel.table.item(layer, 1).text() == "0.2500"
        assert panel.table.item(layer, 2).text() == "288.15"


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["soil_model"] = None

    panel = LandSurfacePanel(registry, dispatcher)

    assert not hasattr(panel, "button")
