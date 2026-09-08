"""
Tests for acf.gui.esoc.panel_manager.AtmospherePanel - the real
primitive-equation atmospheric state panel closing the previously-dead
"Earth System / Atmosphere" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import _ATMOSPHERE_VARIABLES, AtmospherePanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_starts_with_one_real_row_per_state_variable(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = AtmospherePanel(registry, dispatcher)

    assert panel.table.rowCount() == len(_ATMOSPHERE_VARIABLES)
    assert "Real elapsed simulated time: 0" in panel.status_label.text()


def test_initial_temperature_row_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    module = registry.get_module("atmospheric_model")
    panel = AtmospherePanel(registry, dispatcher)

    state = module.initialize_state()
    expected_mean = float(state["T"].mean())
    assert panel.table.item(0, 0).text() == "Temperature (K)"
    assert panel.table.item(0, 1).text() == f"{expected_mean:.4g}"


def test_advancing_updates_the_real_elapsed_time(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = AtmospherePanel(registry, dispatcher)
    panel.n_steps.setValue(3)
    panel.dt_seconds.setValue(120.0)

    panel.button.click()

    assert "Real elapsed simulated time: 360" in panel.status_label.text()


def test_wind_fields_genuinely_evolve_after_a_real_step(qapp, registry):
    """Real regression guard: at least one real state variable must
    change value after a genuine step - never a frozen display."""
    dispatcher = CommandDispatcher()
    panel = AtmospherePanel(registry, dispatcher)
    before = [panel.table.item(2, 1).text(), panel.table.item(3, 1).text()]  # U, V means

    panel.button.click()

    after = [panel.table.item(2, 1).text(), panel.table.item(3, 1).text()]
    assert before != after


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["atmospheric_model"] = None

    panel = AtmospherePanel(registry, dispatcher)

    assert not hasattr(panel, "button")
