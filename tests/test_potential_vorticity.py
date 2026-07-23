import pytest

from acf.science.potential_vorticity import (
    PotentialVorticity,
)


def test_positive():

    value = PotentialVorticity.calculate(
        relative_vorticity=2e-5,
        coriolis=1e-4,
        dtheta_dp=-0.002,
    )

    assert value == pytest.approx(
        2.3544e-06,
        rel=1e-6,
    )


def test_category():

    assert (
        PotentialVorticity.category(5e-7)
        == "Weak"
    )

    assert (
        PotentialVorticity.category(2e-6)
        == "Moderate"
    )

    assert (
        PotentialVorticity.category(1e-5)
        == "Strong"
    )
