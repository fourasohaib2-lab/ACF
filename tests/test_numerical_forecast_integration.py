"""
REWRITTEN: every *_step() method used to ignore its own `state`
argument and return a fixed constant (299.8/11.5/1005.0/14.0/4.5 -
suspiciously close to the near-identical fake constants found and
fixed in the sibling model4d.physics.data_assimilation_engine module
earlier this session) regardless of the real state passed in. Unlike
that module's real OI/BLUE blend (computable in closed form from two
point values), a real forecast time-integration step needs the
spatial grid and physical parameterization tendencies, not just a
single state snapshot - so each step now honestly raises
NotImplementedError instead of returning an invented number.
integrate_timestep() was already genuinely real (returns
state.timestep) and its test is unchanged.
"""

import pytest

from acf.model4d.physics.numerical_forecast_integration import (
    ForecastState,
    NumericalForecastIntegration,
)


def create_state():

    return ForecastState(
        temperature=300,
        humidity=12,
        pressure=100000,
        wind_speed=10,
        precipitation=3,
        timestep=1.0,
    )


def test_temperature_step_not_implemented():

    model = NumericalForecastIntegration()

    with pytest.raises(NotImplementedError):
        model.temperature_step(create_state())


def test_humidity_step_not_implemented():

    model = NumericalForecastIntegration()

    with pytest.raises(NotImplementedError):
        model.humidity_step(create_state())


def test_pressure_step_not_implemented():

    model = NumericalForecastIntegration()

    with pytest.raises(NotImplementedError):
        model.pressure_step(create_state())


def test_wind_step_not_implemented():

    model = NumericalForecastIntegration()

    with pytest.raises(NotImplementedError):
        model.wind_step(create_state())


def test_precipitation_step_not_implemented():

    model = NumericalForecastIntegration()

    with pytest.raises(NotImplementedError):
        model.precipitation_step(create_state())


def test_integrate_timestep():
    """Genuinely real - echoes state.timestep. Unaffected by this fix."""

    model = NumericalForecastIntegration()

    assert model.integrate_timestep(create_state()) == 1.0


def test_forecast_cycle_no_longer_fabricates():

    model = NumericalForecastIntegration()

    result = model.forecast_cycle(create_state())

    assert result["status"] == "NOT_EXECUTED_NO_DYNAMICAL_CORE_CONNECTED"
    assert result["is_real_data"] is False


def test_forecast_stability_index_no_longer_fabricates():

    model = NumericalForecastIntegration()

    assert model.forecast_stability_index(create_state()) is None
