from acf.model4d.physics.observation_quality_control_engine import (
    ObservationQualityControlEngine,
    ObservationQualityControlState,
)


def create_state():

    return ObservationQualityControlState(
        synop_quality=90,
        metar_quality=88,
        radiosonde_quality=95,
        radar_quality=92,
        satellite_quality=89,
        temporal_consistency=96,
        spatial_consistency=94,
        observation_quality=9,
        temperature=290,
        humidity=60,
    )


def test_synop_quality_score():

    model = ObservationQualityControlEngine()

    assert model.synop_quality_score(create_state()) == 81.0


def test_metar_quality_score():

    model = ObservationQualityControlEngine()

    assert model.metar_quality_score(create_state()) == 77.44


def test_radiosonde_quality_score():

    model = ObservationQualityControlEngine()

    assert model.radiosonde_quality_score(create_state()) == 87.4


def test_radar_quality_score():

    model = ObservationQualityControlEngine()

    assert model.radar_quality_score(create_state()) == 83.72


def test_satellite_quality_score():

    model = ObservationQualityControlEngine()

    assert model.satellite_quality_score(create_state()) == 79.21


def test_temporal_consistency():

    model = ObservationQualityControlEngine()

    assert model.temporal_consistency(create_state()) == 91.2


def test_spatial_consistency():

    model = ObservationQualityControlEngine()

    assert model.spatial_consistency(create_state()) == 89.3


def test_observation_reliability():

    model = ObservationQualityControlEngine()

    assert model.observation_reliability(create_state()) == 84.18


def test_quality_control_update():

    model = ObservationQualityControlEngine()

    result = model.quality_control_update(create_state())

    assert result["synop"] == 81.0
    assert result["metar"] == 77.44
    assert result["radiosonde"] == 87.4
    assert result["radar"] == 83.72
    assert result["satellite"] == 79.21
    assert result["temporal"] == 91.2
    assert result["spatial"] == 89.3
    assert result["reliability"] == 84.18
    assert result["outlier"] is False
    assert result["quality_index"] == 7.58


def test_quality_index():

    model = ObservationQualityControlEngine()

    assert model.quality_index(create_state()) == 7.58
