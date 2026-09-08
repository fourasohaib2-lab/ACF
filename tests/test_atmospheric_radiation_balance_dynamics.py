from acf.model4d.physics.atmospheric_radiation_balance_dynamics import (
    AtmosphericRadiationBalanceDynamics,
    RadiationState,
)


def create_state():

    return RadiationState(
        solar_radiation=100,
        infrared_radiation=50,
        greenhouse_gas=4,
        atmospheric_absorption=0.5,
        cloud_fraction=0.8,
        temperature=20,
    )


def test_solar_absorption():

    model = AtmosphericRadiationBalanceDynamics()

    assert model.solar_absorption(create_state()) == 5.0


def test_greenhouse_effect():

    model = AtmosphericRadiationBalanceDynamics()

    assert model.greenhouse_effect(create_state()) == 2.0


def test_cloud_feedback():

    model = AtmosphericRadiationBalanceDynamics()

    assert model.cloud_radiative_feedback(create_state()) == 4.0


def test_radiative_equilibrium():

    model = AtmosphericRadiationBalanceDynamics()

    assert model.radiative_equilibrium(create_state()) == 4.25
