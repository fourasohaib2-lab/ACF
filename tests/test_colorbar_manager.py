from acf.maps.styles.colorbar_manager import ColorBarManager


def test_creation():
    manager = ColorBarManager()

    assert manager.count() == 0


def test_add():
    manager = ColorBarManager()

    obj = object()

    manager.add("temperature", obj)

    assert manager.exists("temperature")


def test_get():
    manager = ColorBarManager()

    obj = object()

    manager.add("temperature", obj)

    assert manager.get("temperature") is obj


def test_remove():
    manager = ColorBarManager()

    manager.add("temperature", object())

    manager.remove("temperature")

    assert not manager.exists("temperature")


def test_names():
    manager = ColorBarManager()

    manager.add("temperature", object())
    manager.add("pressure", object())

    assert manager.names() == ["pressure", "temperature"]


def test_count():
    manager = ColorBarManager()

    manager.add("a", object())
    manager.add("b", object())

    assert manager.count() == 2


def test_clear():
    manager = ColorBarManager()

    manager.add("temperature", object())

    manager.clear()

    assert manager.count() == 0


def test_repr():
    manager = ColorBarManager()

    assert "ColorBarManager" in repr(manager)
