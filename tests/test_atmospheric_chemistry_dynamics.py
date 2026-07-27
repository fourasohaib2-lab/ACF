from acf.model4d.physics.atmospheric_chemistry_dynamics import (
    AtmosphericChemistryDynamics,
    AtmosphericChemistryState,
)


def create_state():

    return AtmosphericChemistryState(
        ozone=5,
        nox=2,
        methane=4,
        carbon_dioxide=10,
        solar_radiation=50,
        temperature=20,
    )


def test_ozone_concentration():

    model = AtmosphericChemistryDynamics()

    assert model.ozone_concentration(create_state()) == 2.5



def test_nox_reaction_rate():

    model = AtmosphericChemistryDynamics()

    assert model.nox_reaction_rate(create_state()) == 2.0



def test_methane_lifetime():

    model = AtmosphericChemistryDynamics()

    assert model.methane_lifetime_effect(create_state()) == 0.01



def test_co2_forcing():

    model = AtmosphericChemistryDynamics()

    assert model.carbon_dioxide_forcing(create_state()) == 0.1



def test_photochemical_activity():

    model = AtmosphericChemistryDynamics()

    assert model.photochemical_activity(create_state()) == 5.5



def test_total_chemical_forcing():

    model = AtmosphericChemistryDynamics()

    assert model.chemical_climate_forcing(create_state()) == 5.6

