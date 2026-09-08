import pytest

from acf.science.dewpoint import DewPoint


def test_dewpoint():

    dew = DewPoint.calculate(20.0, 50.0)

    assert round(dew, 1) == 9.3


def test_dewpoint_rejects_out_of_range_relative_humidity():
    """
    DewPoint.calculate() expects relative_humidity as a PERCENTAGE in
    (0, 100], the opposite convention from the sibling
    WetBulbTemperature.calculate() (a FRACTION in [0, 1]) - out-of-range
    input must raise rather than silently produce a nonsense dewpoint.
    """
    with pytest.raises(ValueError):
        DewPoint.calculate(20.0, 0.0)
    with pytest.raises(ValueError):
        DewPoint.calculate(20.0, 150.0)
    with pytest.raises(ValueError):
        DewPoint.calculate(20.0, -10.0)
