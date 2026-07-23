from acf.maps.contours import Contours


def test_creation():
    c = Contours()

    assert c.count() == 0


def test_set_levels():
    c = Contours()

    c.set_levels(
        "pressure",
        [980, 990, 1000, 1010],
    )

    assert c.exists("pressure")
    assert c.get_levels("pressure") == [
        980,
        990,
        1000,
        1010,
    ]


def test_remove():
    c = Contours()

    c.set_levels(
        "temperature",
        [-20, -10, 0],
    )

    c.remove("temperature")

    assert not c.exists("temperature")


def test_variables():
    c = Contours()

    c.set_levels(
        "temperature",
        [0, 10],
    )

    c.set_levels(
        "pressure",
        [1000, 1010],
    )

    assert "temperature" in c.variables()
    assert "pressure" in c.variables()


def test_clear():
    c = Contours()

    c.set_levels("temperature", [0])
    c.set_levels("pressure", [1000])

    c.clear()

    assert c.count() == 0
