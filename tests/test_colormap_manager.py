from acf.maps.styles.colormap_manager import ColormapManager


def test_creation():

    manager = ColormapManager()

    assert manager.count() == 0


def test_add():

    manager = ColormapManager()

    manager.add("temperature", "coolwarm")

    assert manager.exists("temperature")


def test_get():

    manager = ColormapManager()

    manager.add("temperature", "coolwarm")

    assert manager.get("temperature") == "coolwarm"


def test_remove():

    manager = ColormapManager()

    manager.add("temperature", "coolwarm")

    manager.remove("temperature")

    assert not manager.exists("temperature")


def test_names():

    manager = ColormapManager()

    manager.add("temperature", "coolwarm")
    manager.add("pressure", "viridis")

    assert manager.names() == [
        "pressure",
        "temperature",
    ]


def test_count():

    manager = ColormapManager()

    manager.add("a", "x")
    manager.add("b", "y")

    assert manager.count() == 2


def test_clear():

    manager = ColormapManager()

    manager.add("temperature", "coolwarm")

    manager.clear()

    assert manager.count() == 0


def test_repr():

    manager = ColormapManager()

    assert "ColormapManager" in repr(manager)
