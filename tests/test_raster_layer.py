from acf.maps.layers.raster_layer import RasterLayer


def test_creation():
    layer = RasterLayer("Temperature")

    assert layer.name == "Temperature"
    assert layer.data is None
    assert layer.visible is True
    assert layer.opacity == 1.0


def test_set_data():
    layer = RasterLayer("Temperature")

    values = [10, 12, 15]

    layer.set_data(values)

    assert layer.get_data() == values


def test_visibility():
    layer = RasterLayer()

    layer.set_visible(False)

    assert layer.is_visible() is False


def test_opacity():
    layer = RasterLayer()

    layer.set_opacity(0.5)

    assert layer.opacity == 0.5


def test_clear():
    layer = RasterLayer()

    layer.set_data([1, 2, 3])

    layer.clear()

    assert layer.data is None


def test_repr():
    layer = RasterLayer("Temperature")

    assert "RasterLayer" in repr(layer)
