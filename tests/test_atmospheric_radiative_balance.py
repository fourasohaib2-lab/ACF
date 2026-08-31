from acf.model4d.physics.atmospheric_radiative_balance import (
    AtmosphericRadiativeBalance,
    RadiativeState,
)


def test_net_radiation():

    model = AtmosphericRadiativeBalance()

    state = RadiativeState(
        solar_input=240,
        infrared_output=230,
        greenhouse_forcing=5,
        atmospheric_absorption=2,
    )

    assert model.net_radiation(state) == 17


def test_greenhouse_effect():

    model = AtmosphericRadiativeBalance()

    state = RadiativeState(
        solar_input=200,
        infrared_output=190,
        greenhouse_forcing=4,
        atmospheric_absorption=0.5,
    )

    assert model.greenhouse_effect(state) == 6


def test_energy_balance_warming():

    model = AtmosphericRadiativeBalance()

    state = RadiativeState(
        solar_input=250,
        infrared_output=200,
        greenhouse_forcing=10,
        atmospheric_absorption=5,
    )

    assert model.energy_balance_status(state) == "warming"


def test_energy_balance_cooling():

    model = AtmosphericRadiativeBalance()

    state = RadiativeState(
        solar_input=150,
        infrared_output=250,
        greenhouse_forcing=5,
        atmospheric_absorption=0,
    )

    assert model.energy_balance_status(state) == "cooling"
