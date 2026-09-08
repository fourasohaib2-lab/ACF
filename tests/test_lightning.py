import pytest

from acf.model4d.physics.lightning import Lightning


def test_energy():
    assert Lightning.electric_energy(100, 2, 3) == 600


def test_energy_invalid():
    with pytest.raises(ValueError):
        Lightning.electric_energy(-1, 2, 3)


def test_flash_density():
    assert Lightning.flash_density(20, 10) == 2


def test_flash_density_invalid():
    with pytest.raises(ValueError):
        Lightning.flash_density(10, 0)


def test_storm_index():
    assert Lightning.storm_index(10, 2, 3) == 60


def test_storm_index_invalid():
    with pytest.raises(ValueError):
        Lightning.storm_index(-1, 2, 3)


def test_charge_separation():
    assert Lightning.charge_separation(5, 4) == 20


def test_charge_invalid():
    with pytest.raises(ValueError):
        Lightning.charge_separation(-1, 2)


def test_probability():
    value = Lightning.lightning_probability(100)
    assert round(value, 2) == 0.5


def test_probability_zero():
    assert Lightning.lightning_probability(0) == 0
