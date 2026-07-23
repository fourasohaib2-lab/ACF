from acf.science.saturation_vapor_pressure import (
    SaturationVaporPressure,
)


def test_zero_degree():
    es = SaturationVaporPressure.calculate(0.0)

    assert round(es, 3) == 6.112


def test_twenty_degree():
    es = SaturationVaporPressure.calculate(20.0)

    assert round(es, 2) == 23.37


def test_negative_temperature():
    es = SaturationVaporPressure.calculate(-10.0)

    assert es > 0
