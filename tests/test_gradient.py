from acf.model4d.operators.gradient import Gradient


def test_forward():
    assert Gradient.forward(10, 20) == 10


def test_backward():
    assert Gradient.backward(10, 20) == 10


def test_centered():
    assert Gradient.centered(10, 20) == 5


def test_spacing():
    assert Gradient.forward(0, 20, 2) == 10


def test_negative():
    assert Gradient.forward(20, 10) == -10


def test_zero():
    assert Gradient.forward(5, 5) == 0


def test_magnitude_2d():
    assert Gradient.magnitude(3, 4) == 5


def test_magnitude_3d():
    assert Gradient.magnitude(2, 3, 6) == 7
