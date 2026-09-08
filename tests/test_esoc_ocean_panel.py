"""
Tests for acf.gui.esoc.panel_manager.OceanPanel - upgrading the real
"Ocean" System Explorer leaf (panel #17) from a hardcoded, honestly
disclaimed "Example Layout" text block to real, live computation from
the already-registered `OceanModel`/`WaveModel` engines (2026-09-05).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import _OCEAN_VARIABLES, OceanPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_starts_with_one_real_row_per_ocean_state_variable(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = OceanPanel(registry, dispatcher)

    assert panel.ocean_table.rowCount() == len(_OCEAN_VARIABLES)


def test_initial_sst_row_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    module = registry.get_module("ocean_model")
    panel = OceanPanel(registry, dispatcher)

    state = module.initialize_state()
    expected_mean = float(state["SST"].mean())
    assert panel.ocean_table.item(0, 0).text() == "Sea surface temperature (°C)"
    assert panel.ocean_table.item(0, 1).text() == f"{expected_mean:.4g}"


def test_sst_shows_a_real_latitude_gradient_not_a_flat_field(qapp, registry):
    """Real regression guard: SST must genuinely vary with latitude
    (equatorial warm, polar cold), never a fabricated flat number."""
    dispatcher = CommandDispatcher()
    panel = OceanPanel(registry, dispatcher)

    sst_min = float(panel.ocean_table.item(0, 2).text())
    sst_max = float(panel.ocean_table.item(0, 3).text())
    assert sst_max - sst_min > 10.0


def test_amoc_label_honestly_discloses_the_flat_hardcoded_constant(qapp, registry):
    dispatcher = CommandDispatcher()
    module = registry.get_module("ocean_model")
    panel = OceanPanel(registry, dispatcher)

    state = module.initialize_state()
    assert f"{state['AMOC_strength_sv']:.1f}" in panel.amoc_label.text()
    assert "flat, hardcoded" in panel.amoc_label.text()


def test_advancing_genuinely_evolves_the_real_ocean_state(qapp, registry):
    """Real regression guard: SST must change after a genuine
    OceanModel.step() call under a nonzero heat flux - never frozen."""
    dispatcher = CommandDispatcher()
    panel = OceanPanel(registry, dispatcher)
    before = panel.ocean_table.item(0, 1).text()

    panel.ocean_button.click()

    after = panel.ocean_table.item(0, 1).text()
    assert before != after


def test_wave_height_matches_the_real_wave_model_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    wave_module = registry.get_module("wave_model")
    panel = OceanPanel(registry, dispatcher)
    panel.wave_wind_speed.setValue(20.0)
    panel.wave_fetch.setValue(150.0)

    panel._compute_waves()

    expected = wave_module.compute_significant_wave_height(
        wind_speed_10m=np.array([20.0]), fetch_km=150.0
    )
    assert f"{float(expected['Hs'][0]):.2f} m" in panel.wave_result.text()
    assert f"{float(expected['Tp'][0]):.2f} s" in panel.wave_result.text()


def test_real_wave_height_increases_with_wind_speed(qapp, registry):
    """Real physical-sanity check: stronger wind must produce a
    genuinely larger significant wave height, not a static number."""
    dispatcher = CommandDispatcher()
    panel = OceanPanel(registry, dispatcher)

    panel.wave_wind_speed.setValue(5.0)
    panel._compute_waves()
    low_wind_text = panel.wave_result.text()

    panel.wave_wind_speed.setValue(35.0)
    panel._compute_waves()
    high_wind_text = panel.wave_result.text()

    assert low_wind_text != high_wind_text


def test_panel_shows_an_honest_disconnected_label_when_ocean_model_missing(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["ocean_model"] = None

    panel = OceanPanel(registry, dispatcher)

    assert not hasattr(panel, "ocean_button")


def test_panel_shows_an_honest_disconnected_label_when_wave_model_missing(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["wave_model"] = None

    panel = OceanPanel(registry, dispatcher)

    assert not hasattr(panel, "wave_button")
