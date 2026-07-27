from acf.model4d.physics.atmospheric_chemistry_aerosol_coupling import (
    AtmosphericChemistryAerosolCouplingPhysics
)


def test_pm25():
    assert (
        AtmosphericChemistryAerosolCouplingPhysics.pm25_concentration(
            100,
            20
        )
        == 80
    )


def test_pm10_fraction():
    assert (
        AtmosphericChemistryAerosolCouplingPhysics.pm10_fraction(
            100,
            40
        )
        == 60
    )


def test_sulfate_formation():
    assert (
        AtmosphericChemistryAerosolCouplingPhysics.sulfate_aerosol_formation(
            50,
            0.2
        )
        == 10
    )


def test_black_carbon_effect():
    assert (
        AtmosphericChemistryAerosolCouplingPhysics.black_carbon_radiative_effect(
            20,
            0.5
        )
        == 10
    )


def test_cloud_nucleation():
    assert (
        AtmosphericChemistryAerosolCouplingPhysics.aerosol_cloud_nucleation(
            1000,
            0.1
        )
        == 100
    )


def test_feedback():
    assert (
        AtmosphericChemistryAerosolCouplingPhysics.chemistry_radiative_feedback(
            10,
            2
        )
        == 20
    )


def test_status():

    status = (
        AtmosphericChemistryAerosolCouplingPhysics.module_status()
    )

    assert status["status"] == "active"


def test_negative_pm25():

    try:
        AtmosphericChemistryAerosolCouplingPhysics.pm25_concentration(
            -1,
            0
        )
        assert False
    except ValueError:
        assert True


def test_invalid_ratio():

    try:
        AtmosphericChemistryAerosolCouplingPhysics.black_carbon_radiative_effect(
            10,
            2
        )
        assert False
    except ValueError:
        assert True


def test_invalid_pm():

    try:
        AtmosphericChemistryAerosolCouplingPhysics.pm10_fraction(
            20,
            30
        )
        assert False
    except ValueError:
        assert True
