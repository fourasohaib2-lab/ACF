from acf.model4d.operators.laplacian import Laplacian


def test_positive():
    value = Laplacian.calculate(
        d2_dx2=2e-5,
        d2_dy2=1e-5,
    )
    assert value == 3e-5


def test_negative():
    assert Laplacian.compute(-2, 2) == 0


def test_category():
    assert Laplacian.category(1e-6) == "Weak"
    assert Laplacian.category(2e-5) == "Moderate"
    assert Laplacian.category(8e-5) == "Strong"


def test_horizontal():
    assert Laplacian.horizontal(2, 3) == 5


def test_vertical():
    assert Laplacian.vertical(4) == 4


def test_compute_2d():
    assert Laplacian.compute(2, 3) == 5


def test_compute_3d():
    assert Laplacian.compute(2, 3, 4) == 9


def test_zero():
    assert Laplacian.compute(0, 0, 0) == 0


def test_single():
    assert Laplacian.compute(7) == 7


def test_float():
    assert Laplacian.compute(1.5, 2.5, 3.0) == 7.0
