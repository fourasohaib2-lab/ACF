from acf.science.thermodynamics import Thermodynamics


def test_available():

    data = Thermodynamics.available()

    assert "temperature" in data
    assert "dewpoint" in data
    assert "relative_humidity" in data
