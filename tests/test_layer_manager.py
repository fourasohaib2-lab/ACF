from acf.maps.layer_manager import LayerManager
from acf.maps.layers.raster_layer import RasterLayer


def test_creation():
    manager = LayerManager()

    assert manager.count() == 0


def test_add():
    manager = LayerManager()

    layer = RasterLayer("Temperature")

    manager.add(layer)

    assert manager.count() == 1


def test_get():
    manager = LayerManager()

    layer = RasterLayer("Temperature")

    manager.add(layer)

    assert manager.get("Temperature") is layer


def test_remove():
    manager = LayerManager()

    layer = RasterLayer("Temperature")

    manager.add(layer)

    manager.remove("Temperature")

    assert manager.count() == 0


def test_exists():
    manager = LayerManager()

    manager.add(RasterLayer("Temperature"))

    assert manager.exists("Temperature")


def test_names():
    manager = LayerManager()

    manager.add(RasterLayer("Temperature"))
    manager.add(RasterLayer("Pressure"))

    assert len(manager.names()) == 2


def test_hide():
    manager = LayerManager()

    layer = RasterLayer("Temperature")

    manager.add(layer)

    manager.hide("Temperature")

    assert layer.visible is False


def test_show():
    manager = LayerManager()

    layer = RasterLayer("Temperature")

    layer.set_visible(False)

    manager.add(layer)

    manager.show("Temperature")

    assert layer.visible is True


def test_clear():
    manager = LayerManager()

    manager.add(RasterLayer("Temperature"))

    manager.clear()

    assert manager.count() == 0


def test_repr():
    manager = LayerManager()

    assert "LayerManager" in repr(manager)
