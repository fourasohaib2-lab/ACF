from acf.model4d.physics.observation_bias_correction_engine import (
    ObservationBiasCorrectionEngine,
    ObservationBiasCorrectionState,
)


def create_state():

    return ObservationBiasCorrectionState(
        satellite_bias=20,
        radar_bias=18,
        synop_bias=16,
        metar_bias=15,
        radiosonde_bias=14,
        temperature=290,
        humidity=60,
        observation_quality=8,
    )


def test_satellite_bias_score():

    model = ObservationBiasCorrectionEngine()

    assert model.satellite_bias_score(create_state()) == 18.0


def test_radar_bias_score():

    model = ObservationBiasCorrectionEngine()

    assert model.radar_bias_score(create_state()) == 15.84


def test_synop_bias_score():

    model = ObservationBiasCorrectionEngine()

    assert model.synop_bias_score(create_state()) == 14.56


def test_metar_bias_score():

    model = ObservationBiasCorrectionEngine()

    assert model.metar_bias_score(create_state()) == 13.35


def test_radiosonde_bias_score():

    model = ObservationBiasCorrectionEngine()

    assert model.radiosonde_bias_score(create_state()) == 13.02


def test_temperature_bias():

    model = ObservationBiasCorrectionEngine()

    assert model.temperature_bias(create_state()) == 0.2


def test_humidity_bias():

    model = ObservationBiasCorrectionEngine()

    assert model.humidity_bias(create_state()) == 0.5


def test_systematic_bias():

    model = ObservationBiasCorrectionEngine()

    assert model.systematic_bias(create_state()) == 14.95


def test_bias_correction_update():

    model = ObservationBiasCorrectionEngine()

    result = model.bias_correction_update(create_state())

    assert result["satellite"] == 18.0
    assert result["radar"] == 15.84
    assert result["synop"] == 14.56
    assert result["metar"] == 13.35
    assert result["radiosonde"] == 13.02
    assert result["temperature_bias"] == 0.2
    assert result["humidity_bias"] == 0.5
    assert result["systematic_bias"] == 14.95
    assert result["corrected_observation"] == 14.25
    assert result["bias_index"] == 11.4


def test_bias_index():

    model = ObservationBiasCorrectionEngine()

    assert model.bias_index(create_state()) == 11.4
