"""
Tests for acf.gui.esoc.panel_manager.SpaceWeatherPanel - upgrading the
real "Space Weather" leaf (panel #22) from a hardcoded, honestly
disclaimed "Example Layout" text block to real computation chaining
the real, previously-unused acf.space_weather formula engines
(SolarWindEngine, GeomagneticEngine, IonosphereEngine, SolarFlareEngine
- see tests/test_space_weather_platform.py for their own unit coverage)
(2026-09-06, Phase 54).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import SpaceWeatherPanel
from acf.space_weather.geomagnetism.geomagnetic_engine import GeomagneticEngine, GeomagneticStormScale
from acf.space_weather.ionosphere.ionosphere_engine import IonosphereEngine, RadioBlackoutScale
from acf.space_weather.solar.solar_database import SolarFlareEngine
from acf.space_weather.solar_wind.solar_wind_engine import InterplanetaryMagneticField, SolarWindEngine


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
    panel = SpaceWeatherPanel(registry, dispatcher)

    speed, density, bz, by = 420.0, 5.0, -2.0, 0.0
    pdyn = SolarWindEngine.dynamic_pressure_npa(speed, density)
    imf = InterplanetaryMagneticField(bx_nt=0.0, by_nt=by, bz_nt=bz, total_b_nt=(by**2 + bz**2) ** 0.5)
    reconnection = SolarWindEngine.evaluate_reconnection_risk(imf)
    rmp_re = GeomagneticEngine.magnetopause_standoff_distance_re(pdyn, bz)
    kp_class = GeomagneticStormScale.classify_kp_index(3.0)
    gnss_delay_m = IonosphereEngine.gnss_range_delay_meters(24.5)

    text = panel.result.toPlainText()
    assert f"{pdyn:.3f} nPa" in text
    assert f"{reconnection['clock_angle_deg']}" in text
    assert f"{rmp_re:.2f} Re" in text
    assert kp_class["noaa_scale"] in text
    assert f"{gnss_delay_m:.2f} m" in text


def test_more_negative_bz_increases_the_real_reconnection_risk_and_changes_standoff(qapp, registry):
    """Real physical-sanity check: a stronger southward IMF Bz must
    genuinely raise reconnection risk (Southward Bz reconnects with
    Earth's northward field) and change the computed magnetopause
    standoff distance."""
    dispatcher = CommandDispatcher()
    panel = SpaceWeatherPanel(registry, dispatcher)

    panel.imf_bz.setValue(1.0)  # northward - low risk
    panel._compute()
    quiet_text = panel.result.toPlainText()
    assert "LOW / NORTHWARD BZ" in quiet_text

    panel.imf_bz.setValue(-25.0)  # strongly southward - critical risk
    panel._compute()
    storm_text = panel.result.toPlainText()
    assert "CRITICAL" in storm_text

    assert quiet_text != storm_text


def test_higher_tec_increases_the_real_computed_gnss_delay(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = SpaceWeatherPanel(registry, dispatcher)

    panel.tec.setValue(5.0)
    panel._compute()
    low_tec_delay = IonosphereEngine.gnss_range_delay_meters(5.0)
    assert f"{low_tec_delay:.2f} m" in panel.result.toPlainText()

    panel.tec.setValue(150.0)
    panel._compute()
    high_tec_delay = IonosphereEngine.gnss_range_delay_meters(150.0)
    assert f"{high_tec_delay:.2f} m" in panel.result.toPlainText()

    assert high_tec_delay > low_tec_delay


def test_higher_kp_index_reaches_a_more_severe_real_noaa_scale(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = SpaceWeatherPanel(registry, dispatcher)

    panel.kp_index.setValue(1.0)
    panel._compute()
    assert "G0" in panel.result.toPlainText()

    panel.kp_index.setValue(9.0)
    panel._compute()
    assert "G5" in panel.result.toPlainText()


def test_higher_xray_flux_reaches_a_more_severe_real_flare_class_and_blackout(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = SpaceWeatherPanel(registry, dispatcher)

    panel.xray_flux.setValue(1e-7)
    panel._compute()
    quiet_text = panel.result.toPlainText()
    assert "R0" in quiet_text

    panel.xray_flux.setValue(5e-3)
    panel._compute()
    extreme_text = panel.result.toPlainText()
    assert "X" in SolarFlareEngine.classify_goes_xray_flare(5e-3)["flare_class"]
    assert "R5" in extreme_text
    assert RadioBlackoutScale.classify_xray_radio_blackout(5e-3)["radio_blackout_scale"] in extreme_text
