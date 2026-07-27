from acf.model4d.physics.atmospheric_carbon_cycle_dynamics import (
    AtmosphericCarbonCycleDynamics,
    CarbonCycleState,
)


def test_natural_sink():

    model = AtmosphericCarbonCycleDynamics()

    state = CarbonCycleState(
        emissions=100,
        ocean_uptake=30,
        vegetation_uptake=20
    )

    assert model.natural_sink(state) == 50


def test_carbon_change():

    model = AtmosphericCarbonCycleDynamics()

    state = CarbonCycleState(
        emissions=100,
        ocean_uptake=30,
        vegetation_uptake=20
    )

    assert model.atmospheric_carbon_change(state) == 50


def test_increasing_carbon():

    model = AtmosphericCarbonCycleDynamics()

    state = CarbonCycleState(
        emissions=100,
        ocean_uptake=20,
        vegetation_uptake=10
    )

    assert model.carbon_state(state) == "increasing"


def test_stable_carbon():

    model = AtmosphericCarbonCycleDynamics()

    state = CarbonCycleState(
        emissions=50,
        ocean_uptake=30,
        vegetation_uptake=20
    )

    assert model.carbon_state(state) == "stable"
