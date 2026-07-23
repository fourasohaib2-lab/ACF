from acf.maps.streamlines import Streamlines


def test_creation():
    s = Streamlines()
    assert s.count() == 0


def test_add():
    s = Streamlines()

    s.add("wind", [1, 2], [3, 4])

    assert s.exists("wind")
    assert s.count() == 1


def test_get():
    s = Streamlines()

    s.add("wind", [10], [20])

    data = s.get("wind")

    assert data["u"] == [10]
    assert data["v"] == [20]


def test_remove():
    s = Streamlines()

    s.add("wind", [1], [2])

    s.remove("wind")

    assert not s.exists("wind")


def test_clear():
    s = Streamlines()

    s.add("wind", [1], [2])
    s.add("jet", [3], [4])

    s.clear()

    assert s.count() == 0


def test_names():
    s = Streamlines()

    s.add("wind", [1], [2])
    s.add("jet", [3], [4])

    names = s.names()

    assert "wind" in names
    assert "jet" in names
