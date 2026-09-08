import pytest

from acf.model4d.physics.aerosol_chemistry import AerosolChemistryPhysics


def test_aerosol_mass():

    value = AerosolChemistryPhysics.aerosol_mass(1000, 1e-6, 1000)

    assert round(value, 12) == 0.000000004


def test_hygroscopic_growth():

    value = AerosolChemistryPhysics.hygroscopic_growth(2, 50)

    assert value == 2.5


def test_deposition_velocity():

    value = AerosolChemistryPhysics.dry_deposition_velocity(0.01)

    assert value == 10


def test_conversion():

    value = AerosolChemistryPhysics.chemical_conversion(100, 0.25)

    assert value == 25


def test_activation():

    value = AerosolChemistryPhysics.cloud_activation_fraction(500, 1000)

    assert value == 0.5


def test_activation_limit():

    value = AerosolChemistryPhysics.cloud_activation_fraction(2000, 1000)

    assert value == 1


def test_negative_mass():
    with pytest.raises(ValueError):
        AerosolChemistryPhysics.aerosol_mass(-1, 1e-6, 1000)


def test_negative_humidity():
    with pytest.raises(ValueError):
        AerosolChemistryPhysics.hygroscopic_growth(1, -10)


def test_invalid_size():
    with pytest.raises(ValueError):
        AerosolChemistryPhysics.dry_deposition_velocity(0)


def test_invalid_threshold():
    with pytest.raises(ValueError):
        AerosolChemistryPhysics.cloud_activation_fraction(10, 0)
