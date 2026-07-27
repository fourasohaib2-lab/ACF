from acf.model4d.physics.atmospheric_chemistry import (
    AtmosphericChemistryPhysics
)


def test_reaction_rate():

    value = AtmosphericChemistryPhysics.reaction_rate(
        2,
        3,
        4
    )

    assert value == 24



def test_ozone_production():

    value = AtmosphericChemistryPhysics.ozone_production(
        2,
        5
    )

    assert value == 15



def test_photolysis_rate():

    value = AtmosphericChemistryPhysics.photolysis_rate(
        0.5,
        20
    )

    assert value == 10



def test_chemical_lifetime():

    value = AtmosphericChemistryPhysics.chemical_lifetime(
        100,
        5
    )

    assert value == 20



def test_mixing_ratio():

    value = AtmosphericChemistryPhysics.mixing_ratio_concentration(
        1,
        1000
    )

    assert value == 1000



def test_decay():

    value = AtmosphericChemistryPhysics.exponential_decay(
        100,
        10,
        10
    )

    assert round(value, 2) == 36.79



def test_methane_lifetime():

    value = AtmosphericChemistryPhysics.methane_lifetime(
        200,
        10
    )

    assert value == 20



def test_ozone_column():

    value = AtmosphericChemistryPhysics.ozone_column_density(
        300,
        1000
    )

    assert value == 300



def test_arrhenius():

    value = AtmosphericChemistryPhysics.arrhenius_rate(
        1000,
        300
    )

    assert round(value, 3) == 0.670



def test_aerosol_effect():

    value = AtmosphericChemistryPhysics.aerosol_effect(
        2,
        3
    )

    assert value == 6
