"""Unit tests for ACF Scientific MapCanvas, dataset ingestion, and ViewManager integration."""

import os

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

# Ensure QApplication is initialized offscreen for tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_map_projection_manager():
    import cartopy.crs as ccrs

    from acf.gui.map.map_projection import MapProjection

    proj_mgr = MapProjection("2D Mercator Map")
    assert isinstance(proj_mgr.current_crs, ccrs.CRS)

    crs_ortho = proj_mgr.set_projection("Orthographic Projection")
    assert isinstance(crs_ortho, ccrs.Orthographic)

    crs_lambert = proj_mgr.set_projection("Lambert Conformal Conic")
    assert isinstance(crs_lambert, ccrs.LambertConformal)


def test_map_layer_manager():
    from acf.data.dataset import Dataset
    from acf.gui.map.map_layers import LayerManager

    layer_mgr = LayerManager()
    assert "Satellite RGB" in layer_mgr.get_active_layers()

    layer_mgr.set_active_layers(["Radar Mosaic", "2m Temp"])
    assert layer_mgr.get_active_layers() == ["Radar Mosaic", "2m Temp"]

    # Test real dataset binding
    ds = Dataset("nwp_run_01")
    ds.add_variable("t2m", np.ones((50, 100)) * 290.0)
    layer_mgr.bind_dataset(ds)
    assert layer_mgr.current_dataset == ds


def test_map_canvas_widget(qapp):
    from acf.data.dataset import Dataset
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    assert canvas.figure is not None
    assert canvas.axes is not None

    # Test ACF-MAP-004 APIs
    canvas.set_projection("Orthographic Projection")
    canvas.set_active_layers(["Wind Vectors", "MSLP"])
    canvas.draw_world()

    canvas.label.setText("Test Map Title")
    assert canvas.title_text == "Test Map Title"

    # Test ACF-MAP-005 Data Binding
    ds = Dataset("wrf_forecast")
    ds.add_variable("t2m", np.ones((40, 80)) * 295.0)
    canvas.load_dataset(ds)
    qapp.processEvents()
    canvas.close()
    qapp.processEvents()
