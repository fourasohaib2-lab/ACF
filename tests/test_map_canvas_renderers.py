from acf.maps.canvas import MapCanvas


def test_raster_renderer():

    canvas = MapCanvas()

    assert canvas.raster_renderer is not None


def test_contour_renderer():

    canvas = MapCanvas()

    assert canvas.contour_renderer is not None


def test_wind_renderer():

    canvas = MapCanvas()

    assert canvas.wind_renderer is not None
