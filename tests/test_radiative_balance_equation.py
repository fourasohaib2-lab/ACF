from acf.model4d.physics.radiative_balance_equation import (
    RadiativeBalanceEquation,
    RadiativeBalanceState,
)


def test_absorbed_energy():

    model = RadiativeBalanceEquation()

    state = RadiativeBalanceState(
        solar_input=100,
        albedo=0.3,
        outgoing_longwave=50
    )

    assert model.absorbed_solar_energy(state) == 70


def test_energy_balance():

    model = RadiativeBalanceEquation()

    state = RadiativeBalanceState(
        solar_input=100,
        albedo=0.2,
        outgoing_longwave=50
    )

    assert model.energy_balance(state) == 30


def test_warming_state():

    model = RadiativeBalanceEquation()

    state = RadiativeBalanceState(
        solar_input=100,
        albedo=0.1,
        outgoing_longwave=50
    )

    assert model.climate_state(state) == "warming"


def test_equilibrium_state():

    model = RadiativeBalanceEquation()

    state = RadiativeBalanceState(
        solar_input=100,
        albedo=0.5,
        outgoing_longwave=50
    )

    assert model.climate_state(state) == "equilibrium"
