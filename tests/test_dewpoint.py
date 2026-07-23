from acf.science.dewpoint import DewPoint


def test_dewpoint():

    dew = DewPoint.calculate(20.0, 50.0)

    assert round(dew, 1) == 9.3
