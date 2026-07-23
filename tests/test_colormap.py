from acf.maps.colormap import ColorMap


def test_creation():
    cmap = ColorMap()
    assert cmap is not None


def test_temperature():
    cmap = ColorMap()
    assert cmap.get("temperature") == "coolwarm"


def test_pressure():
    cmap = ColorMap()
    assert cmap.get("pressure") == "viridis"


def test_exists():
    cmap = ColorMap()
    assert cmap.exists("humidity")
    assert not cmap.exists("unknown")


def test_add():
    cmap = ColorMap()

    cmap.add("snow", "winter")

    assert cmap.exists("snow")


def test_remove():
    cmap = ColorMap()

    cmap.add("snow", "winter")
    cmap.remove("snow")

    assert not cmap.exists("snow")


def test_count():
    cmap = ColorMap()

    assert cmap.count() >= 10
