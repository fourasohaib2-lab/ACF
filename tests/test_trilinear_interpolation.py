from acf.model4d.interpolation.trilinear import TrilinearInterpolation


def test_center():

    value = TrilinearInterpolation.interpolate(
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        0.5,
        0.5,
        0.5,
    )

    assert value == 35


def test_bottom():

    value = TrilinearInterpolation.interpolate(
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        0.5,
        0.5,
        0,
    )

    assert value == 15


def test_top():

    value = TrilinearInterpolation.interpolate(
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        0.5,
        0.5,
        1,
    )

    assert value == 55


def test_corner():

    value = TrilinearInterpolation.interpolate(
        5,
        10,
        15,
        20,
        25,
        30,
        35,
        40,
        0,
        0,
        0,
    )

    assert value == 5


def test_upper_corner():

    value = TrilinearInterpolation.interpolate(
        5,
        10,
        15,
        20,
        25,
        30,
        35,
        40,
        1,
        1,
        1,
    )

    assert value == 40
