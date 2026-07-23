from acf.maps.canvas import MapCanvas


def test_creation():
    canvas = MapCanvas()

    assert canvas.figure is not None
    assert canvas.axes is not None
    assert canvas.renderer is not None


def test_initialize():
    canvas = MapCanvas()

    assert canvas.axes.get_title() == "Atmospheric Complexity Framework"


def test_clear_canvas():
    canvas = MapCanvas()

    canvas.clear_canvas()

    assert canvas.axes is not None


def test_plot_demo():
    canvas = MapCanvas()

    canvas.plot_demo()

    assert canvas.axes.get_title() == "Demo Plot"
