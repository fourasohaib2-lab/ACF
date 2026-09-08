from acf.model4d.operators.advection import Advection


def test_compute_2d():

    value = Advection.compute(velocity=(2, 3), gradient=(4, 5))

    assert value == 23


def test_compute_3d():

    value = Advection.compute(velocity=(1, 2, 3), gradient=(4, 5, 6))

    assert value == 32


def test_horizontal():

    assert Advection.horizontal(2, 4, 3, 5) == 23


def test_vertical():

    assert Advection.vertical(4, 5) == 20


def test_zero():

    assert Advection.compute(velocity=(0, 0, 0), gradient=(1, 2, 3)) == 0


def test_single():

    assert Advection.compute(velocity=(5,), gradient=(2,)) == 10


def test_float():

    assert Advection.compute(velocity=(1.5, 2.5), gradient=(2, 4)) == 13


def test_negative():

    assert Advection.compute(velocity=(-2, 2), gradient=(3, -3)) == -12


def test_category():

    assert Advection.category(1e-7) == "Weak"
    assert Advection.category(5e-6) == "Moderate"
    assert Advection.category(2e-5) == "Strong"


def test_category_negative():

    assert Advection.category(-2e-5) == "Strong"
