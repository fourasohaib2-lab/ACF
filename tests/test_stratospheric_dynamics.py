from acf.model4d.physics.stratospheric_dynamics import (
    StratosphericDynamics,
    StratosphericState,
)


def test_initialization():

    model = StratosphericDynamics()

    assert model.name == "Stratospheric Dynamics"


def test_state_creation():

    state = StratosphericState(wind_speed=50, temperature_gradient=20)

    assert state.wind_speed == 50
    assert state.hemisphere == "north"


def test_stability():

    model = StratosphericDynamics()

    state = StratosphericState(wind_speed=40, temperature_gradient=10)

    result = model.calculate_stability(state)

    assert result > 1


def test_circulation():

    model = StratosphericDynamics()

    state = StratosphericState(wind_speed=40, temperature_gradient=10, stability_index=2)

    result = model.calculate_circulation_strength(state)

    assert result == 80


def test_ozone():

    model = StratosphericDynamics()

    state = StratosphericState(wind_speed=30, temperature_gradient=5, ozone_level=400)

    assert model.ozone_feedback(state) == 0.4


def test_simulation():

    model = StratosphericDynamics()

    state = StratosphericState(wind_speed=60, temperature_gradient=15)

    result = model.simulate(state)

    assert "circulation_strength" in result


def test_hemisphere():

    state = StratosphericState(wind_speed=30, temperature_gradient=10, hemisphere="south")

    assert state.hemisphere == "south"


def test_default_values():

    state = StratosphericState(wind_speed=20, temperature_gradient=5)

    assert state.stability_index == 1.0


def test_negative_gradient():

    model = StratosphericDynamics()

    state = StratosphericState(wind_speed=20, temperature_gradient=-5)

    assert model.calculate_stability(state) < 1


def test_complete_model():

    model = StratosphericDynamics()

    state = StratosphericState(wind_speed=70, temperature_gradient=25, ozone_level=350)

    result = model.simulate(state)

    assert result["module"] == "Stratospheric Dynamics"
