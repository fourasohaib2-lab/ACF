from acf.model4d.physics.atmospheric_radiation_transfer import (
    AtmosphericRadiationTransfer,
    RadiationState,
)


def create_state():

    return RadiationState(
        solar_input=100,
        infrared_output=80,
        atmospheric_absorption=0.2,
        greenhouse_gas_effect=0.5,
        aerosol_loading=0.3,
        surface_temperature=300,
    )


def test_solar_absorption():

    model = AtmosphericRadiationTransfer()

    assert model.solar_radiation_absorption(create_state()) == 20


def test_infrared_trapping():

    model = AtmosphericRadiationTransfer()

    assert model.infrared_trapping(create_state()) == 40


def test_rayleigh_scattering():

    model = AtmosphericRadiationTransfer()

    assert model.rayleigh_scattering(create_state()) == 13


def test_outgoing_longwave():

    model = AtmosphericRadiationTransfer()

    assert model.outgoing_longwave_radiation(create_state()) == 80


def test_greenhouse_feedback():

    model = AtmosphericRadiationTransfer()

    assert model.greenhouse_feedback(create_state()) == 1.5


def test_energy_balance():

    model = AtmosphericRadiationTransfer()

    assert model.radiative_energy_balance(create_state()) == -20
