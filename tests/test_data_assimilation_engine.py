from acf.model4d.physics.data_assimilation_engine import (
    DataAssimilationEngine,
    ObservationState,
    ModelState,
)


def create_model():

    return ModelState(
        temperature=300,
        humidity=10,
        pressure=100000,
        wind_speed=10,
        precipitation=3,
    )


def create_observation():

    return ObservationState(
        temperature=299,
        humidity=12,
        pressure=100800,
        wind_speed=14,
        precipitation=5,
    )


def test_temperature_analysis():

    model = DataAssimilationEngine()

    assert (
        model.temperature_analysis(
            create_model(),
            create_observation()
        )
        == 299.5
    )


def test_humidity_analysis():

    model = DataAssimilationEngine()

    assert (
        model.humidity_analysis(
            create_model(),
            create_observation()
        )
        == 11.8
    )


def test_pressure_analysis():

    model = DataAssimilationEngine()

    assert (
        model.pressure_analysis(
            create_model(),
            create_observation()
        )
        == 1008.0
    )


def test_wind_analysis():

    model = DataAssimilationEngine()

    assert (
        model.wind_analysis(
            create_model(),
            create_observation()
        )
        == 13.5
    )


def test_precipitation_analysis():

    model = DataAssimilationEngine()

    assert (
        model.precipitation_analysis(
            create_model(),
            create_observation()
        )
        == 4.2
    )


def test_innovation_score():

    model = DataAssimilationEngine()

    assert (
        model.innovation_score(
            create_model(),
            create_observation()
        )
        == 2.5
    )


def test_assimilation_cycle():

    model = DataAssimilationEngine()

    result = model.assimilation_cycle(
        create_model(),
        create_observation()
    )

    assert result["temperature"] == 299.5
    assert result["humidity"] == 11.8


def test_analysis_quality_index():

    model = DataAssimilationEngine()

    assert (
        model.analysis_quality_index(
            create_model(),
            create_observation()
        )
        == 96.5
    )
