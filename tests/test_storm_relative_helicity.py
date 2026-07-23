import pytest

from acf.science.storm_relative_helicity import (
    StormRelativeHelicity,
)


def test_srh():

    value = StormRelativeHelicity.calculate(
        u=20,
        v=10,
        storm_u=10,
        storm_v=5,
        du=3,
        dv=4,
    )

    assert value == pytest.approx(25)


def test_category():

    assert StormRelativeHelicity.category(50) == "Weak"

    assert StormRelativeHelicity.category(150) == "Moderate"

    assert StormRelativeHelicity.category(300) == "Strong"

    assert StormRelativeHelicity.category(500) == "Extreme"
