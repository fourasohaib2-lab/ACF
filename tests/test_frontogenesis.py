import pytest

from acf.science.frontogenesis import Frontogenesis


def test_frontogenesis():

    value = Frontogenesis.calculate(
        temperature_gradient=2e-5,
        deformation=2.0,
    )

    assert value == pytest.approx(4e-5)


def test_negative_gradient():

    value = Frontogenesis.calculate(
        temperature_gradient=-2e-5,
        deformation=2.0,
    )

    assert value == pytest.approx(4e-5)


def test_category():

    assert Frontogenesis.category(1e-6) == "Weak"
    assert Frontogenesis.category(2e-5) == "Moderate"
    assert Frontogenesis.category(8e-5) == "Strong"
