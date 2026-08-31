"""
REWRITTEN: cloud_radar_interaction() was already genuinely real (uses
state.cloud_cover and state.radar_reflectivity) - its test is
unchanged. Every OTHER method used to ignore its own `state` argument
and return a fixed constant (13.0/2.5/0.1/4.4/10.0/25.5) regardless of
the real state passed in - same bug shape as the already-fixed
model4d.physics.numerical_forecast_integration.NumericalForecastIntegration.
A real fusion weight/correction factor needs a calibrated data-fusion
model, not just a single point state - so each now honestly raises
NotImplementedError (or returns None for fusion_index()).
atmospheric_state_update() used to aggregate the fake values into one
result; it now honestly reports the one genuinely real computation
(cloud_radar_interaction) and an honest status for the rest.
"""

import pytest

from acf.model4d.physics.satellite_radar_fusion_engine import (
    SatelliteRadarFusionEngine,
    SatelliteRadarState,
)


def create_state():

    return SatelliteRadarState(
        temperature=290,
        humidity=15,
        cloud_cover=30,
        radar_reflectivity=40,
        satellite_radiance=200,
        wind_speed=12,
        precipitation=5,
        observation_quality=8,
    )


def test_observation_weight_not_implemented():

    model = SatelliteRadarFusionEngine()

    with pytest.raises(NotImplementedError):
        model.observation_weight(create_state())


def test_radar_signal_adjustment_not_implemented():

    model = SatelliteRadarFusionEngine()

    with pytest.raises(NotImplementedError):
        model.radar_signal_adjustment(create_state())


def test_satellite_temperature_correction_not_implemented():

    model = SatelliteRadarFusionEngine()

    with pytest.raises(NotImplementedError):
        model.satellite_temperature_correction(create_state())


def test_humidity_radar_satellite_fusion_not_implemented():

    model = SatelliteRadarFusionEngine()

    with pytest.raises(NotImplementedError):
        model.humidity_radar_satellite_fusion(create_state())


def test_precipitation_detection_not_implemented():

    model = SatelliteRadarFusionEngine()

    with pytest.raises(NotImplementedError):
        model.precipitation_detection(create_state())


def test_cloud_radar_interaction():
    """Genuinely real - uses state.cloud_cover and state.radar_reflectivity. Unaffected by this fix."""

    model = SatelliteRadarFusionEngine()
    state = create_state()

    expected = state.cloud_cover * 0.1 + state.radar_reflectivity * 0.05
    assert model.cloud_radar_interaction(state) == expected


def test_atmospheric_state_update_no_longer_fabricates():

    model = SatelliteRadarFusionEngine()
    state = create_state()

    result = model.atmospheric_state_update(state)

    assert result["status"] == "PARTIAL_ONLY_CLOUD_RADAR_INTERACTION_IS_REAL"
    assert result["is_real_data"] is False
    assert result["cloud_radar_interaction"] == model.cloud_radar_interaction(state)


def test_fusion_index_no_longer_fabricates():

    model = SatelliteRadarFusionEngine()

    assert model.fusion_index(create_state()) is None
