from acf.maps.field import WeatherField


def test_creation():
    field = WeatherField("Temperature")
    assert field.name == "Temperature"
    assert field.count() == 0


def test_add():
    field = WeatherField("Temperature")
    field.add(20)
    field.add(25)
    assert field.count() == 2


def test_minimum():
    field = WeatherField("Temperature", [20, 18, 25])
    assert field.minimum() == 18


def test_maximum():
    field = WeatherField("Temperature", [20, 18, 25])
    assert field.maximum() == 25


def test_mean():
    field = WeatherField("Temperature", [10, 20, 30])
    assert field.mean() == 20


def test_clear():
    field = WeatherField("Temperature", [1, 2, 3])
    field.clear()
    assert field.count() == 0
