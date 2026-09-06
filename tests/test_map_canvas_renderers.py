import numpy as np

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


# CORRECTED (2026-09-06): draw_raster()/draw_contours() used to claim a
# truthy result while no real matplotlib drawing primitive was ever
# called (the canvas never actually changed), and draw_wind(field) used
# to crash with a TypeError (WindRenderer.set_field() needs u AND v,
# not one field). Now all three honestly disclose that no real drawing
# happened, and draw_wind() takes u/v separately without crashing.


def test_draw_raster_honestly_discloses_no_real_rendering():
    canvas = MapCanvas()
    result = canvas.draw_raster(np.zeros((3, 3)))
    assert result["field_set"] is True
    assert result["rendered"] is False
    assert result["status"] == "NOT_RENDERED_NO_REAL_DRAW_CALL_WIRED"


def test_draw_contours_honestly_discloses_no_real_rendering():
    canvas = MapCanvas()
    result = canvas.draw_contours(np.zeros((3, 3)))
    assert result["field_set"] is True
    assert result["rendered"] is False
    assert result["status"] == "NOT_RENDERED_NO_REAL_DRAW_CALL_WIRED"


def test_draw_wind_no_longer_crashes_and_discloses_no_real_rendering():
    canvas = MapCanvas()
    result = canvas.draw_wind(np.zeros((3, 3)), np.zeros((3, 3)))
    assert result["field_set"] is True
    assert result["rendered"] is False
    assert result["status"] == "NOT_RENDERED_NO_REAL_DRAW_CALL_WIRED"
