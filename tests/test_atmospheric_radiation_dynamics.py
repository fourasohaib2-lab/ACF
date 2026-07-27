from acf.model4d.physics.atmospheric_radiation_dynamics import (
    AtmosphericRadiationDynamics,
    RadiationState,
)


def create_state():

    return RadiationState(
        solar_flux=340,
        infrared_flux=240,
        atmospheric_absorption=0.3,
        greenhouse_factor=0.5,
        surface_temperature=288,
        atmospheric_temperature=270,
        emissivity=0.95,
    )



def test_solar_radiation():

    model = AtmosphericRadiationDynamics()

    assert model.solar_radiation(create_state()) == 340



def test_absorbed_radiation():

    model = AtmosphericRadiationDynamics()

    assert model.absorbed_radiation(create_state()) == 102



def test_greenhouse_effect():

    model = AtmosphericRadiationDynamics()

    assert model.greenhouse_effect(create_state()) == 120



def test_outgoing_longwave_radiation():

    model = AtmosphericRadiationDynamics()

    assert model.outgoing_longwave_radiation(create_state()) == 120



def test_radiative_balance():

    model = AtmosphericRadiationDynamics()

    assert model.radiative_balance(create_state()) == -18



def test_radiative_cooling():

    model = AtmosphericRadiationDynamics()

    assert model.radiative_cooling(create_state()) == 2.56



def test_radiative_equilibrium():

    model = AtmosphericRadiationDynamics()

    assert model.radiative_equilibrium(create_state()) == 283



def test_infrared_emission():

    model = AtmosphericRadiationDynamics()

    assert model.infrared_emission(create_state()) > 300
