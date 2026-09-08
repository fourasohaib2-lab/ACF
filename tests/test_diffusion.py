from acf.model4d.operators.diffusion import Diffusion


def test_positive():
    value = Diffusion.calculate(
        laplacian=2e-5,
        coefficient=0.5,
    )
    assert value == 1e-5


def test_negative():
    assert Diffusion.compute(-2, 2) == 0


def test_strength():
    assert Diffusion.strength(1e-7) == "Weak"
    assert Diffusion.strength(5e-6) == "Moderate"
    assert Diffusion.strength(2e-5) == "Strong"


def test_horizontal():
    assert Diffusion.horizontal(2, 3) == 5


def test_vertical():
    assert Diffusion.vertical(4) == 4


def test_compute_2d():
    assert Diffusion.compute(2, 3) == 5


def test_compute_3d():
    assert Diffusion.compute(2, 3, 4) == 9


def test_zero():
    assert Diffusion.compute(0, 0, 0) == 0


def test_single():
    assert Diffusion.compute(7) == 7


def test_float():
    assert Diffusion.compute(1.5, 2.5, 3.0) == 7.0
