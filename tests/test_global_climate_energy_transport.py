from acf.model4d.physics.global_climate_energy_transport import (
    ClimateEnergyState,
    GlobalClimateEnergyTransport,
)


def test_absorbed_energy():

    model = GlobalClimateEnergyTransport()

    state = ClimateEnergyState(
        solar_input=1000,
        outgoing_longwave=200,
        ocean_transport=100,
        atmospheric_transport=100,
    )

    assert model.absorbed_solar_energy(state) == 700


def test_heat_transport():

    model = GlobalClimateEnergyTransport()

    state = ClimateEnergyState(
        solar_input=1000,
        outgoing_longwave=200,
        ocean_transport=150,
        atmospheric_transport=50,
    )

    assert model.total_heat_transport(state) == 200


def test_energy_balance():

    model = GlobalClimateEnergyTransport()

    state = ClimateEnergyState(
        solar_input=1000,
        outgoing_longwave=300,
        ocean_transport=100,
        atmospheric_transport=100,
    )

    assert model.energy_balance(state) == 200


def test_climate_trend():

    model = GlobalClimateEnergyTransport()

    state = ClimateEnergyState(
        solar_input=1000,
        outgoing_longwave=300,
        ocean_transport=100,
        atmospheric_transport=100,
    )

    assert model.climate_trend(state) == "warming"
