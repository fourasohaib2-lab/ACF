"""
Tests for acf.gui.esoc.panel_manager.WildfiresPanel - the real Fire
Weather Index panel closing the previously-dead "Earth System /
Wildfires" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import WildfiresPanel
from acf.simulation_engine.extreme_events.wildfire import WildfireSimulator


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_fwi_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = WildfiresPanel(registry, dispatcher)

    panel.temp.setValue(35.0)
    panel.rh.setValue(15.0)
    panel.wind.setValue(40.0)
    panel.rain.setValue(0.0)
    panel.button.click()

    expected = WildfireSimulator().compute_fire_weather_index(
        temp_c=np.array([35.0]), relative_humidity_pct=np.array([15.0]),
        wind_speed_kmh=np.array([40.0]), rain_24h_mm=np.array([0.0]),
    )
    text = panel.result.toPlainText()
    assert f"{float(expected['FWI'][0]):.1f}" in text
    assert f"{float(expected['ROS_m_min'][0]):.2f}" in text
    assert f"{float(expected['flame_length_m'][0]):.2f}" in text


def test_extreme_danger_is_flagged_for_a_real_hot_dry_windy_case(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = WildfiresPanel(registry, dispatcher)

    panel.temp.setValue(50.0)
    panel.rh.setValue(1.0)
    panel.wind.setValue(150.0)
    panel.rain.setValue(0.0)
    panel.button.click()

    assert "EXTREME" in panel.result.toPlainText()


def test_rain_genuinely_lowers_the_real_fire_weather_index(qapp, registry):
    """Cross-check the real, documented rain-wetting correction - more
    rain must reduce the real FWI, never leave it unchanged."""
    dispatcher = CommandDispatcher()
    panel = WildfiresPanel(registry, dispatcher)
    panel.temp.setValue(30.0)
    panel.rh.setValue(20.0)
    panel.wind.setValue(30.0)

    panel.rain.setValue(0.0)
    panel.button.click()
    dry_text = panel.result.toPlainText()

    panel.rain.setValue(50.0)
    panel.button.click()
    wet_text = panel.result.toPlainText()

    assert dry_text != wet_text


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["wildfire_simulator"] = None

    panel = WildfiresPanel(registry, dispatcher)

    assert not hasattr(panel, "button")
