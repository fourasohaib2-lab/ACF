from acf.model4d.physics.moisture import Moisture


def test_vapor_pressure():
    assert Moisture.vapor_pressure(
        50,
        20
    ) == 10


def test_relative_humidity():
    assert Moisture.relative_humidity(
        10,
        20
    ) == 50


def test_mixing_ratio():
    value = Moisture.mixing_ratio(
        10,
        1000
    )

    assert value > 0


def test_specific_humidity():

    value = Moisture.specific_humidity(
        0.01
    )

    assert value < 0.01


def test_dew_point():

    value = Moisture.dew_point(
        30,
        50
    )

    assert value < 30


def test_category_dry():

    assert Moisture.category(20) == "Dry"


def test_category_moderate():

    assert Moisture.category(50) == "Moderate"


def test_category_humid():

    assert Moisture.category(70) == "Humid"


def test_category_very_humid():

    assert Moisture.category(90) == "Very Humid"


def test_zero():

    assert Moisture.relative_humidity(
        10,
        0
    ) == 0
