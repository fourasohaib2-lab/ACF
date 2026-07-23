from acf.maps.canvas.map_canvas import MapCanvas


def test_canvas_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    assert canvas.axes is not None


def test_plot(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    canvas.plot_demo()

    assert len(canvas.axes.lines) == 1
