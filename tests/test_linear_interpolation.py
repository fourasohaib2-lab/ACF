from acf.model4d.interpolation.linear import LinearInterpolation


def test_linear_middle():

    assert LinearInterpolation.interpolate(
        0,
        0,
        10,
        100,
        5,
    ) == 50


def test_linear_start():

    assert LinearInterpolation.interpolate(
        0,
        10,
        10,
        20,
        0,
    ) == 10


def test_linear_end():

    assert LinearInterpolation.interpolate(
        0,
        10,
        10,
        20,
        10,
    ) == 20


def test_midpoint():

    assert LinearInterpolation.midpoint(
        10,
        20,
    ) == 15


def test_fraction():

    assert LinearInterpolation.fraction(
        0,
        10,
        5,
    ) == 0.5


def test_clamp_inside():

    assert LinearInterpolation.clamp(
        5,
        0,
        10,
    ) == 5


def test_clamp_low():

    assert LinearInterpolation.clamp(
        -5,
        0,
        10,
    ) == 0


def test_clamp_high():

    assert LinearInterpolation.clamp(
        20,
        0,
        10,
    ) == 10


def test_invalid():

    try:
        LinearInterpolation.interpolate(
            1,
            0,
            1,
            10,
            1,
        )
    except ValueError:
        return

    assert False
