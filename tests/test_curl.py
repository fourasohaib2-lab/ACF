from acf.model4d.operators.curl import Curl


def test_calculate():
    result = Curl.calculate(
        dw_dy=5,
        dv_dz=2,
        du_dz=3,
        dw_dx=1,
        dv_dx=4,
        du_dy=1,
    )

    assert result == (3, 2, 3)


def test_compute():
    assert Curl.compute(1, 2, 3) == 6


def test_horizontal():
    assert Curl.horizontal(3, 4) == 5


def test_vertical():
    assert Curl.vertical(5) == 5


def test_magnitude():
    assert Curl.magnitude(3, 4, 0) == 5


def test_normalize():
    assert Curl.normalize(3, 4, 0) == (0.6, 0.8, 0.0)


def test_zero_normalize():
    assert Curl.normalize(0, 0, 0) == (0.0, 0.0, 0.0)


def test_category():
    assert Curl.category(1e-6) == "Weak"
    assert Curl.category(2e-5) == "Moderate"
    assert Curl.category(8e-5) == "Strong"


def test_rotation():
    assert Curl.is_rotating(1, 0, 0)


def test_direction():
    assert Curl.direction(1) == "Counterclockwise"
    assert Curl.direction(-1) == "Clockwise"
    assert Curl.direction(0) == "None"
