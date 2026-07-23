from acf.maps.renderers.raster_renderer import RasterRenderer


def test_creation():
    renderer = RasterRenderer()

    assert renderer.field is None
    assert renderer.colormap == "viridis"


def test_set_field():
    renderer = RasterRenderer()

    renderer.set_field([[1, 2], [3, 4]])

    assert renderer.has_field()


def test_colormap():
    renderer = RasterRenderer()

    renderer.set_colormap("jet")

    assert renderer.colormap == "jet"


def test_range():
    renderer = RasterRenderer()

    renderer.set_range(-20, 40)

    assert renderer.minimum == -20
    assert renderer.maximum == 40


def test_alpha():
    renderer = RasterRenderer()

    renderer.set_alpha(0.5)

    assert renderer.alpha == 0.5


def test_clear():
    renderer = RasterRenderer()

    renderer.set_field([[1]])

    renderer.clear()

    assert renderer.field is None


def test_render():
    renderer = RasterRenderer()

    renderer.set_field([[1]])

    assert renderer.render()


def test_repr():
    renderer = RasterRenderer()

    assert "RasterRenderer" in repr(renderer)
