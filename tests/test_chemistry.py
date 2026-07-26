from acf.model4d.physics.chemistry import Chemistry
import pytest


def test_mixing_ratio():
    value = Chemistry.mixing_ratio(2, 4)
    assert value == 0.5


def test_mixing_ratio_invalid():
    with pytest.raises(ValueError):
        Chemistry.mixing_ratio(1, 0)


def test_reaction_rate():
    value = Chemistry.reaction_rate(2, 3, 4)
    assert value == 24


def test_reaction_rate_invalid():
    with pytest.raises(ValueError):
        Chemistry.reaction_rate(-1, 2, 3)


def test_photolysis_rate():
    value = Chemistry.photolysis_rate(0.5, 10)
    assert value == 5


def test_photolysis_invalid():
    with pytest.raises(ValueError):
        Chemistry.photolysis_rate(-1, 5)


def test_ozone_production():
    value = Chemistry.ozone_production(10, 5, 100)
    assert value > 0


def test_ozone_invalid():
    with pytest.raises(ValueError):
        Chemistry.ozone_production(1, 1, -1)


def test_lifetime():
    value = Chemistry.lifetime(100, 10)
    assert value == 10


def test_lifetime_invalid():
    with pytest.raises(ValueError):
        Chemistry.lifetime(100, 0)
