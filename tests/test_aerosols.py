from acf.model4d.physics.aerosols import Aerosols
import pytest


def test_concentration():
    assert Aerosols.concentration(10, 5) == 2


def test_concentration_invalid():
    with pytest.raises(ValueError):
        Aerosols.concentration(1, 0)


def test_pm25_fraction():
    assert Aerosols.pm25_fraction(20, 100) == 0.2


def test_pm25_invalid():
    with pytest.raises(ValueError):
        Aerosols.pm25_fraction(1, 0)


def test_dry_deposition():
    value = Aerosols.dry_deposition(2, 3, 4)
    assert value == 24


def test_dry_deposition_invalid():
    with pytest.raises(ValueError):
        Aerosols.dry_deposition(1, -1, 2)


def test_wet_deposition():
    assert Aerosols.wet_deposition(10, 2) == 20


def test_wet_deposition_invalid():
    with pytest.raises(ValueError):
        Aerosols.wet_deposition(1, -1)


def test_cloud_interaction():
    assert Aerosols.cloud_interaction(5, 2) == 10


def test_radiative_forcing():
    assert Aerosols.radiative_forcing(0.5) == -65
