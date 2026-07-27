from acf.model4d.physics.ocean_heat_uptake_dynamics import (
    OceanHeatUptakeDynamics,
    OceanHeatState,
)


def test_absorbed_heat():

    model = OceanHeatUptakeDynamics()

    state = OceanHeatState(
        heat_flux=100,
        ocean_capacity=200,
        initial_temperature=10
    )

    assert model.absorbed_heat(state) == 100


def test_temperature_change():

    model = OceanHeatUptakeDynamics()

    state = OceanHeatState(
        heat_flux=100,
        ocean_capacity=200,
        initial_temperature=10
    )

    assert model.temperature_change(state) == 0.5


def test_future_temperature():

    model = OceanHeatUptakeDynamics()

    state = OceanHeatState(
        heat_flux=100,
        ocean_capacity=200,
        initial_temperature=10
    )

    assert model.future_temperature(state) == 10.5


def test_high_memory():

    model = OceanHeatUptakeDynamics()

    state = OceanHeatState(
        heat_flux=50,
        ocean_capacity=500,
        initial_temperature=15
    )

    assert model.climate_memory(state) == "high_memory"
