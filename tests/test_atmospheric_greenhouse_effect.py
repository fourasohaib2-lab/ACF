from acf.model4d.physics.atmospheric_greenhouse_effect import (
    AtmosphericGreenhouseEffect,
    GreenhouseState,
)


def test_absorbed_infrared():

    model = AtmosphericGreenhouseEffect()

    state = GreenhouseState(infrared_emission=100, greenhouse_gas_factor=0.5)

    assert model.absorbed_infrared(state) == 50


def test_total_forcing():

    model = AtmosphericGreenhouseEffect()

    state = GreenhouseState(infrared_emission=100, greenhouse_gas_factor=0.5, atmospheric_reemission=20)

    assert model.total_greenhouse_forcing(state) == 70


def test_warming_response():

    model = AtmosphericGreenhouseEffect()

    state = GreenhouseState(infrared_emission=100, greenhouse_gas_factor=0.2)

    assert model.climate_response(state) == "warming"


def test_neutral_response():

    model = AtmosphericGreenhouseEffect()

    state = GreenhouseState(infrared_emission=0, greenhouse_gas_factor=0)

    assert model.climate_response(state) == "neutral"
