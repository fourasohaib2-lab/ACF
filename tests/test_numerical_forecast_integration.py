from acf.model4d.physics.numerical_forecast_integration import (
    NumericalForecastIntegration,
    ForecastState,
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


def test_temperature_step():

    model = NumericalForecastIntegration()

    assert model.temperature_step(create_state()) == 299.8


def test_humidity_step():

    model = NumericalForecastIntegration()

    assert model.humidity_step(create_state()) == 11.5


def test_pressure_step():

    model = NumericalForecastIntegration()

    assert model.pressure_step(create_state()) == 1005.0


def test_wind_step():

    model = NumericalForecastIntegration()

    assert model.wind_step(create_state()) == 14.0


def test_precipitation_step():

    model = NumericalForecastIntegration()

    assert model.precipitation_step(create_state()) == 4.5


def test_integrate_timestep():

    model = NumericalForecastIntegration()

    assert model.integrate_timestep(create_state()) == 1.0


def test_forecast_cycle():

    model = NumericalForecastIntegration()

    result = model.forecast_cycle(create_state())

    assert result["temperature"] == 299.8
    assert result["humidity"] == 11.5


def test_forecast_stability_index():

    model = NumericalForecastIntegration()

    assert model.forecast_stability_index(create_state()) == 98.5
