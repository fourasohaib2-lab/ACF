from acf.maps.projections.projection_manager import ProjectionManager


def test_creation():
    manager = ProjectionManager()

    assert manager.count() == 0


def test_add():
    manager = ProjectionManager()

    obj = object()

    manager.add("PlateCarree", obj)

    assert manager.count() == 1


def test_get():
    manager = ProjectionManager()

    obj = object()

    manager.add("Mercator", obj)

    assert manager.get("Mercator") is obj


def test_exists():
    manager = ProjectionManager()

    manager.add("Mercator", object())

    assert manager.exists("Mercator")


def test_remove():
    manager = ProjectionManager()

    manager.add("Mercator", object())

    manager.remove("Mercator")

    assert manager.count() == 0


def test_default():
    manager = ProjectionManager()

    obj = object()

    manager.add("PlateCarree", obj)

    assert manager.default() is obj


def test_set_default():
    manager = ProjectionManager()

    p1 = object()
    p2 = object()

    manager.add("PlateCarree", p1)
    manager.add("Mercator", p2)

    manager.set_default("Mercator")

    assert manager.default() is p2


def test_names():
    manager = ProjectionManager()

    manager.add("A", object())
    manager.add("B", object())

    assert len(manager.names()) == 2


def test_clear():
    manager = ProjectionManager()

    manager.add("A", object())

    manager.clear()

    assert manager.count() == 0


def test_repr():
    manager = ProjectionManager()

    assert "ProjectionManager" in repr(manager)
