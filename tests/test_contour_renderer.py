from acf.maps.renderers.contour_renderer import ContourRenderer


def test_creation():
    renderer = ContourRenderer()

    assert renderer.field is None
    assert renderer.levels == []


def test_set_field():
    renderer = ContourRenderer()

    renderer.set_field([[1, 2], [3, 4]])

    assert renderer.has_field()


def test_levels():
    renderer = ContourRenderer()

    renderer.set_levels([0, 5, 10])

    assert renderer.levels == [0, 5, 10]


def test_color():
    renderer = ContourRenderer()

    renderer.set_color("blue")

    assert renderer.color == "blue"


def test_linewidth():
    renderer = ContourRenderer()

    renderer.set_linewidth(2.5)

    assert renderer.linewidth == 2.5


def test_clear():
    renderer = ContourRenderer()

    renderer.set_field([1])
    renderer.set_levels([1, 2])

    renderer.clear()

    assert renderer.field is None
    assert renderer.levels == []


def test_render():
    renderer = ContourRenderer()

    renderer.set_field([1])

    assert renderer.render()


def test_repr():
    renderer = ContourRenderer()

    assert "ContourRenderer" in repr(renderer)
