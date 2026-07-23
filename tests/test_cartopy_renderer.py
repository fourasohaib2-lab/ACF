from acf.maps.canvas.map_canvas import MapCanvas


def test_renderer_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    assert canvas.renderer is not None
