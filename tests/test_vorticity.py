import pytest

from acf.science.vorticity import Vorticity


def test_positive():

    value = Vorticity.calculate(
        dv_dx=3e-5,
        du_dy=1e-5,
    )

    assert value == pytest.approx(2e-5)


def test_negative():

    value = Vorticity.calculate(
        dv_dx=1e-5,
        du_dy=3e-5,
    )

    assert value == pytest.approx(-2e-5)


def test_category():

    assert Vorticity.category(1e-6) == "Weak"
    assert Vorticity.category(2e-5) == "Moderate"
    assert Vorticity.category(8e-5) == "Strong"
