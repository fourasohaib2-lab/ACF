"""
Tests for acf.gui.esoc.panel_manager.CryospherePanel - upgrading the
real "Cryosphere" leaf (panel #19) from a hardcoded, honestly
disclaimed "Example Layout" text block to real computation chaining
SeaIceThermodynamics (Stefan's law), OceanSeaIceCoupling (already-
audited ocean-to-ice heat flux), and PermafrostThawModel (already
flagged as illustrative-only - see reports/ACF_MASTER_AUDIT_v2.md)
(2026-09-06, Phase 55).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.earth_physics.cryosphere_physics.permafrost import PermafrostThawModel
from acf.earth_physics.cryosphere_physics.sea_ice import SeaIceThermodynamics
from acf.earth_physics.ocean_physics.sea_ice_interaction import OceanSeaIceCoupling
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import CryospherePanel


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
    panel = CryospherePanel(registry, dispatcher)

    growth_rate_m_s = SeaIceThermodynamics.ice_growth_rate_m_s(-20.0, 1.8, -1.8)
    expected_cm_day = growth_rate_m_s * 86400.0 * 100.0
    heat_flux = OceanSeaIceCoupling.compute_heat_flux_to_ice(-1.0, -1.8)
    ch4 = PermafrostThawModel.compute_ch4_emission_megatons(0.021)

    text = panel.result.toPlainText()
    assert f"{expected_cm_day:.3f} cm/day" in text
    assert f"{heat_flux:.2f} W/m" in text
    assert f"{ch4:.3f} Mt" in text
    assert "illustrative order-of-magnitude only" in text


def test_thicker_ice_genuinely_slows_the_real_growth_rate(qapp, registry):
    """Stefan's law physical-sanity check: growth rate must be inversely
    proportional to current ice thickness (this is the exact bug a
    prior audit found and fixed in SeaIceThermodynamics itself)."""
    dispatcher = CommandDispatcher()
    panel = CryospherePanel(registry, dispatcher)

    panel.ice_thickness.setValue(0.1)
    panel._compute()
    thin_text = panel.result.toPlainText()

    panel.ice_thickness.setValue(3.0)
    panel._compute()
    thick_text = panel.result.toPlainText()

    assert thin_text != thick_text
    thin_rate = SeaIceThermodynamics.ice_growth_rate_m_s(-20.0, 0.1, -1.8)
    thick_rate = SeaIceThermodynamics.ice_growth_rate_m_s(-20.0, 3.0, -1.8)
    assert thin_rate > thick_rate


def test_surface_temp_above_freezing_shows_no_real_growth(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = CryospherePanel(registry, dispatcher)

    panel.surface_temp.setValue(5.0)  # above the default freezing point
    panel._compute()

    assert "0.000 cm/day" in panel.result.toPlainText()
    assert "no growth" in panel.result.toPlainText()


def test_warmer_ocean_increases_the_real_heat_flux_to_ice(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = CryospherePanel(registry, dispatcher)

    panel.ocean_temp.setValue(-1.5)
    panel._compute()
    cold_text = panel.result.toPlainText()

    panel.ocean_temp.setValue(10.0)
    panel._compute()
    warm_text = panel.result.toPlainText()

    assert cold_text != warm_text
    assert OceanSeaIceCoupling.compute_heat_flux_to_ice(10.0, -1.8) > OceanSeaIceCoupling.compute_heat_flux_to_ice(
        -1.5, -1.8
    )
