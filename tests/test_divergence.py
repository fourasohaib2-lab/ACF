import pytest

from acf.model4d.operators.divergence import Divergence as ModelDivergence
from acf.science.divergence import Divergence


def test_positive():

    value = Divergence.calculate(
        du_dx=3e-5,
        dv_dy=1e-5,
    )

    assert value == pytest.approx(4e-5)


def test_negative():

    value = Divergence.calculate(
        du_dx=-3e-5,
        dv_dy=-1e-5,
    )

    assert value == pytest.approx(-4e-5)


def test_category():

    assert Divergence.category(1e-6) == "Weak"
    assert Divergence.category(2e-5) == "Moderate"
    assert Divergence.category(8e-5) == "Strong"


def test_horizontal():
    assert ModelDivergence.horizontal(2, 3) == 5


def test_vertical():
    assert ModelDivergence.vertical(4) == 4


def test_compute_2d():
    assert ModelDivergence.compute(2, 3) == 5


def test_compute_3d():
    assert ModelDivergence.compute(2, 3, 4) == 9


def test_negative_2():
    assert ModelDivergence.compute(-2, 2) == 0


def test_zero():
    assert ModelDivergence.compute(0, 0, 0) == 0


def test_single():
    assert ModelDivergence.compute(7) == 7


def test_float():
    assert ModelDivergence.compute(1.5, 2.5, 3.0) == 7.0
