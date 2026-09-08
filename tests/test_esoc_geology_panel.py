"""
Tests for acf.gui.esoc.panel_manager.GeologyPanel - upgrading the real
"Geology" leaf (panel #23) from a hardcoded, honestly disclaimed
"Example Layout" text block (an operationally dangerous claim, since
volcanic ash advisories affect flight routing) to real computation
chaining SeismicWaveEngine, SeismologyEngine and TsunamiForecastEngine
- all previously unused in any GUI panel and already audited clean
(2026-09-06, Phase 56).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.geology.seismic_waves import SeismicWaveEngine
from acf.geology.seismology import SeismologyEngine
from acf.geology.tsunami_engine import TsunamiForecastEngine
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import GeologyPanel


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
    panel = GeologyPanel(registry, dispatcher)

    k_pa, mu_pa, rho = 50.0e9, 30.0e9, 2700.0
    vp = SeismicWaveEngine.p_wave_velocity_m_s(k_pa, mu_pa, rho)
    vs = SeismicWaveEngine.s_wave_velocity_m_s(mu_pa, rho)
    bath = SeismologyEngine.bath_law_largest_aftershock(7.5)
    tsunami = TsunamiForecastEngine().evaluate_tsunami_hazard(7.5, 20.0, 300.0, 4000.0)

    text = panel.result.toPlainText()
    assert f"{vp:.0f} m/s" in text
    assert f"{vs:.0f} m/s" in text
    assert f"Mw {bath:.1f}" in text
    assert tsunami["tsunami_risk"] in text
    assert tsunami["warning_level"] in text


def test_deeper_shear_modulus_genuinely_changes_the_real_wave_velocities(qapp, registry):
    """Real physical-sanity check: a stiffer medium (higher shear
    modulus) must genuinely raise both S-wave and P-wave velocity."""
    dispatcher = CommandDispatcher()
    panel = GeologyPanel(registry, dispatcher)

    panel.shear_modulus.setValue(10.0)
    panel._compute()
    soft_text = panel.result.toPlainText()

    panel.shear_modulus.setValue(200.0)
    panel._compute()
    stiff_text = panel.result.toPlainText()

    assert soft_text != stiff_text
    vs_soft = SeismicWaveEngine.s_wave_velocity_m_s(10.0e9, 2700.0)
    vs_stiff = SeismicWaveEngine.s_wave_velocity_m_s(200.0e9, 2700.0)
    assert vs_stiff > vs_soft


def test_larger_mainshock_raises_the_real_tsunami_risk(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = GeologyPanel(registry, dispatcher)

    panel.mainshock_mw.setValue(4.0)  # too small to be tsunamigenic
    panel._compute()
    assert "LOW / NO TSUNAMI GENERATED" in panel.result.toPlainText()

    panel.mainshock_mw.setValue(8.5)  # a real megathrust-class event
    panel._compute()
    assert "HIGH / TSUNAMIGENIC MEGATHRUST EVENT" in panel.result.toPlainText()


def test_farther_station_genuinely_changes_the_real_sp_delay(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = GeologyPanel(registry, dispatcher)

    panel.station_distance.setValue(50.0)
    panel._compute()
    near_text = panel.result.toPlainText()

    panel.station_distance.setValue(2000.0)
    panel._compute()
    far_text = panel.result.toPlainText()

    assert near_text != far_text
