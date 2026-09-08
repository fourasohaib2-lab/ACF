from acf.model4d.interpolation.bilinear import BilinearInterpolation


def test_center():

    value = BilinearInterpolation.interpolate(
        0,
        10,
        20,
        30,
        0.5,
        0.5,
    )

    assert value == 15


def test_corner():

    value = BilinearInterpolation.interpolate(
        5,
        10,
        20,
        30,
        0,
        0,
    )

    assert value == 5


def test_right():

    value = BilinearInterpolation.interpolate(
        0,
        100,
        0,
        100,
        1,
        0.5,
    )

    assert value == 100


def test_left():

    value = BilinearInterpolation.interpolate(
        10,
        20,
        30,
        40,
        0,
        0.5,
    )

    assert value == 20


def test_top():

    value = BilinearInterpolation.interpolate(
        0,
        20,
        100,
        120,
        0.5,
        1,
    )

    assert value == 110


def test_bottom():

    value = BilinearInterpolation.interpolate(
        0,
        20,
        100,
        120,
        0.5,
        0,
    )

    assert value == 10
