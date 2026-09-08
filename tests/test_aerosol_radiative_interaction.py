import pytest

from acf.model4d.physics.aerosol_radiative_interaction import AerosolRadiativeInteractionPhysics


def test_transmitted_solar_radiation():
    value = AerosolRadiativeInteractionPhysics.transmitted_solar_radiation(1000, 0)
    assert value == 1000


def test_scattering_fraction():
    value = AerosolRadiativeInteractionPhysics.aerosol_scattering_fraction(0.5, 0.8)
    assert value == 0.4


def test_absorption_fraction():
    value = AerosolRadiativeInteractionPhysics.aerosol_absorption_fraction(0.5, 0.2)
    assert value == 0.1


def test_radiative_forcing():
    value = AerosolRadiativeInteractionPhysics.radiative_forcing(100, 0.2)
    assert value == -80


def test_cloud_interaction():
    value = AerosolRadiativeInteractionPhysics.aerosol_cloud_interaction(1000, 0.5)
    assert value == 500


def test_status():
    status = AerosolRadiativeInteractionPhysics.module_status()

    assert status["status"] == "active"


def test_negative_radiation():
    with pytest.raises(ValueError):
        AerosolRadiativeInteractionPhysics.transmitted_solar_radiation(-10, 1)


def test_negative_optical_depth():
    with pytest.raises(ValueError):
        AerosolRadiativeInteractionPhysics.aerosol_scattering_fraction(-1, 0.5)


def test_invalid_scattering_ratio():
    with pytest.raises(ValueError):
        AerosolRadiativeInteractionPhysics.aerosol_scattering_fraction(1, 2)


def test_invalid_albedo():
    with pytest.raises(ValueError):
        AerosolRadiativeInteractionPhysics.radiative_forcing(10, 2)
