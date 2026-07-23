from acf.science.specific_humidity import SpecificHumidity


def test_specific_humidity():
    q = SpecificHumidity.calculate(0.01)

    assert round(q, 5) == 0.00990


def test_zero():
    assert SpecificHumidity.calculate(0.0) == 0.0
