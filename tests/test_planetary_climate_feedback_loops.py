from acf.model4d.physics.planetary_climate_feedback_loops import (
    ClimateFeedbackState,
    PlanetaryClimateFeedbackLoops,
)


def test_ice_albedo_feedback():

    model = PlanetaryClimateFeedbackLoops()

    state = ClimateFeedbackState(
        temperature_anomaly=2,
        ice_cover=0.5,
        water_vapor=1,
        cloud_effect=0,
        co2_forcing=0,
        ocean_memory=0,
    )

    assert model.ice_albedo_feedback(state) == 1


def test_water_vapor_feedback():

    model = PlanetaryClimateFeedbackLoops()

    state = ClimateFeedbackState(
        temperature_anomaly=2,
        ice_cover=1,
        water_vapor=0.5,
        cloud_effect=0,
        co2_forcing=0,
        ocean_memory=0,
    )

    assert model.water_vapor_feedback(state) == 1


def test_total_feedback():

    model = PlanetaryClimateFeedbackLoops()

    state = ClimateFeedbackState(
        temperature_anomaly=2,
        ice_cover=0.5,
        water_vapor=1,
        cloud_effect=1,
        co2_forcing=2,
        ocean_memory=1,
    )

    assert model.total_feedback(state) == 6


def test_climate_response():

    model = PlanetaryClimateFeedbackLoops()

    state = ClimateFeedbackState(
        temperature_anomaly=2,
        ice_cover=0.2,
        water_vapor=1,
        cloud_effect=1,
        co2_forcing=2,
        ocean_memory=1,
    )

    assert (
        model.climate_response(state)
        == "amplifying warming"
    )
