import pytest

from acf.model4d.physics.mountain_physics import MountainPhysics


def test_orographic_lifting():

    value = MountainPhysics.orographic_lifting(10, 0.1)

    assert round(value, 2) == 1.0


def test_adiabatic_cooling():
    """
    CORRECTED: used to use LAPSE_RATE (0.0065 K/m, the ISA
    environmental/standard-atmosphere rate) for a parcel's own
    adiabatic cooling, which is instead governed by the dry adiabatic
    lapse rate G/CP (~0.00977 K/m) - a materially different (~50%
    steeper) value. G and CP were already defined on this class but
    never actually used anywhere until now.
    """

    value = MountainPhysics.adiabatic_cooling(1000)

    assert round(value, 2) == 9.77


def test_temperature():

    value = MountainPhysics.mountain_temperature(300, 1000)

    assert round(value, 1) == 293.5


def test_precipitation():

    value = MountainPhysics.orographic_precipitation(2, 5)

    assert value == 10


def test_foehn():
    """CORRECTED: same LAPSE_RATE-vs-DRY_ADIABATIC_LAPSE_RATE bug as adiabatic_cooling() - see its NOTE."""

    value = MountainPhysics.foehn_temperature(280, 1000)

    assert round(value, 1) == 289.8


def test_flat():

    assert MountainPhysics.classify_orography(0.01) == "flat"


def test_hill():

    assert MountainPhysics.classify_orography(0.1) == "hill"


def test_mountain():

    assert MountainPhysics.classify_orography(0.5) == "mountain"


def test_negative_height():

    with pytest.raises(ValueError):
        MountainPhysics.adiabatic_cooling(-10)


def test_negative_wind():

    with pytest.raises(ValueError):
        MountainPhysics.orographic_lifting(-1, 0.1)
