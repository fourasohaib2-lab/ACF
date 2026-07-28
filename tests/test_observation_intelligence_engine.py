from acf.model4d.physics.observation_intelligence_engine import (
    ObservationIntelligenceEngine,
    ObservationIntelligenceState,
)


def create_state():

    return ObservationIntelligenceState(
        satellite_signal=80,
        radar_signal=75,
        assimilation_score=90,
        atmospheric_variability=20,
        cloud_confidence=30,
        temperature=290,
        humidity=15,
        observation_quality=8,
    )


def test_observation_confidence_score():

    model = ObservationIntelligenceEngine()

    assert (
        model.observation_confidence_score(create_state())
        == 33.5
    )


def test_multi_sensor_consistency():

    model = ObservationIntelligenceEngine()

    assert (
        model.multi_sensor_consistency(create_state())
        == 9.5
    )


def test_atmospheric_pattern_detection():

    model = ObservationIntelligenceEngine()

    assert (
        model.atmospheric_pattern_detection(create_state())
        == 19.5
    )


def test_observation_uncertainty():

    model = ObservationIntelligenceEngine()

    assert (
        model.observation_uncertainty(create_state())
        == 66.5
    )


def test_model4d_state_assimilation():

    model = ObservationIntelligenceEngine()

    result = model.model4d_state_assimilation(
        create_state()
    )

    assert result["confidence"] == 33.5
    assert result["consistency"] == 9.5
    assert result["pattern"] == 19.5
    assert result["uncertainty"] == 66.5


def test_intelligence_index():

    model = ObservationIntelligenceEngine()

    assert (
        model.intelligence_index(create_state())
        == 20.83
    )
