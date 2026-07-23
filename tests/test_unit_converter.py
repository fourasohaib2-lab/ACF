from acf.data.unit_converter import UnitConverter


def test_kelvin():

    c = UnitConverter()

    assert round(c.convert(300, "K", "°C"), 2) == 26.85


def test_pressure():

    c = UnitConverter()

    assert c.convert(101325, "Pa", "hPa") == 1013.25


def test_wind():

    c = UnitConverter()

    assert round(c.convert(10, "m s-1", "km h-1"), 1) == 36.0


def test_rain():

    c = UnitConverter()

    assert c.convert(1, "m", "mm") == 1000
