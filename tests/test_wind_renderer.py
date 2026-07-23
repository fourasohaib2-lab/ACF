from acf.maps.renderers.wind_renderer import WindRenderer


def test_creation():
    renderer = WindRenderer()

    assert renderer.u is None
    assert renderer.v is None


def test_set_field():
    renderer = WindRenderer()

    renderer.set_field([1, 2], [3, 4])

    assert renderer.has_field()


def test_clear():
    renderer = WindRenderer()

    renderer.set_field([1], [2])
    renderer.clear()

    assert not renderer.has_field()


def test_color():
    renderer = WindRenderer()

    renderer.set_color("red")

    assert renderer.color == "red"


def test_scale():
    renderer = WindRenderer()

    renderer.set_scale(5)

    assert renderer.scale == 5


def test_render():
    renderer = WindRenderer()

    renderer.set_field([1], [2])

    assert renderer.render()


def test_repr():
    renderer = WindRenderer()

    assert "WindRenderer" in repr(renderer)
