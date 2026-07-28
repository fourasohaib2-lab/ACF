from acf.model4d.physics.satellite_radar_fusion_engine import (
    SatelliteRadarState,
    SatelliteRadarFusionEngine,
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


def test_observation_weight():

    model = SatelliteRadarFusionEngine()

    assert (
        model.observation_weight(create_state())
        == 13.0
    )


def test_radar_signal_adjustment():

    model = SatelliteRadarFusionEngine()

    assert (
        model.radar_signal_adjustment(create_state())
        == 2.5
    )


def test_satellite_temperature_correction():

    model = SatelliteRadarFusionEngine()

    assert (
        model.satellite_temperature_correction(create_state())
        == 0.1
    )


def test_humidity_radar_satellite_fusion():

    model = SatelliteRadarFusionEngine()

    assert (
        model.humidity_radar_satellite_fusion(create_state())
        == 4.4
    )


def test_precipitation_detection():

    model = SatelliteRadarFusionEngine()

    assert (
        model.precipitation_detection(create_state())
        == 10.0
    )


def test_atmospheric_state_update():

    model = SatelliteRadarFusionEngine()

    result = model.atmospheric_state_update(
        create_state()
    )

    assert result["observation_weight"] == 13.0
    assert result["precipitation_signal"] == 10.0


def test_fusion_index():

    model = SatelliteRadarFusionEngine()

    assert (
        model.fusion_index(create_state())
        == 25.5
    )
