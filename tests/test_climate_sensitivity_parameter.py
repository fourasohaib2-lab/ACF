from acf.model4d.physics.climate_sensitivity_parameter import (
    ClimateSensitivityParameter,
    ClimateSensitivityState,
)


def test_calculate_sensitivity():

    model = ClimateSensitivityParameter()

    state = ClimateSensitivityState(
        forcing_wm2=2,
        feedback_parameter=1.5
    )

    result = model.calculate_sensitivity(state)

    assert result == 3


def test_equilibrium_factor():

    model = ClimateSensitivityParameter()

    state = ClimateSensitivityState(
        forcing_wm2=2,
        feedback_parameter=1.5,
        equilibrium_factor=2
    )

    result = model.calculate_sensitivity(state)

    assert result == 6


def test_temperature_response():

    model = ClimateSensitivityParameter()

    result = model.temperature_response(
        forcing=2,
        sensitivity=1.5
    )

    assert result == 3


def test_state_creation():

    state = ClimateSensitivityState(
        forcing_wm2=1,
        feedback_parameter=1
    )

    assert state.forcing_wm2 == 1
