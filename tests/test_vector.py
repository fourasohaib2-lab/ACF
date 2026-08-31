from acf.maps.vector import Vector


def test_creation():
    vector = Vector()

    assert vector.count() == 0


def test_add():
    vector = Vector()

    vector.add(
        "wind",
        [10, 20],
        [5, 15],
    )

    assert vector.exists("wind")
    assert vector.count() == 1


def test_get():
    vector = Vector()

    vector.add(
        "wind",
        [1],
        [2],
    )

    data = vector.get("wind")

    assert data["u"] == [1]
    assert data["v"] == [2]


def test_remove():
    vector = Vector()

    vector.add(
        "wind",
        [1],
        [2],
    )

    vector.remove("wind")

    assert not vector.exists("wind")


def test_clear():
    vector = Vector()

    vector.add("wind", [1], [2])
    vector.add("current", [3], [4])

    vector.clear()

    assert vector.count() == 0


def test_names():
    vector = Vector()

    vector.add("wind", [1], [2])
    vector.add("current", [3], [4])

    names = vector.names()

    assert "wind" in names
    assert "current" in names
