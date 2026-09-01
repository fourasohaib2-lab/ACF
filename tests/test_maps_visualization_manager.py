"""
Atmospheric Complexity Framework (ACF)

Test suite for the maps/ visualization pipeline (VisualizationManager ->
AutoRenderer -> DataRenderer -> ScientificRenderer/CartopyRenderer,
BaseLayer, and the layer-manager bookkeeping used by VisualizationManager).

CORRECTED: this whole chain was completely non-functional with zero
test coverage anywhere:
- DataRenderer() crashed on construction (imported
  acf.maps.renderers.cartopy_renderer.CartopyRenderer, which requires
  a real GUI canvas with no default, instead of the canvas-optional
  acf.visualization.cartopy_renderer.CartopyRenderer compatibility
  facade that actually has the create_map()/add_field()/status()
  methods this class calls).
- VisualizationManager() crashed the same way via AutoRenderer's own
  DataRenderer, and separately called create_layer()/remove_layer()/
  status() on acf.maps.layer_manager.LayerManager, which has none of
  those methods (imported the wrong LayerManager - a second,
  unrelated name collision - instead of
  acf.visualization.layer_manager.LayerManager, which does).
- Even past those two, ScientificRenderer.create_layer() constructed
  BaseLayer(name=name, variable=variable), and BaseLayer.__init__()
  only accepted `name` - every real render() call crashed with
  "unexpected keyword argument 'variable'".

See data_renderer.py, visualization_manager.py, and
maps/layers/base_layer.py's own NOTE (correction) docstrings.
"""

import numpy as np
import pytest

from acf.data.dataset import Dataset
from acf.maps.auto_renderer import AutoRenderer
from acf.maps.data_renderer import DataRenderer
from acf.maps.layers.base_layer import BaseLayer
from acf.maps.visualization_manager import VisualizationManager


def _sample_dataset() -> Dataset:
    ds = Dataset(name="test_ds", filetype="NetCDF")
    ds.add_variable("t2m", np.array([1.0, 2.0, 3.0]))
    return ds


def test_base_layer_accepts_variable():
    layer = BaseLayer(name="temperature", variable="t2m")
    assert layer.name == "temperature"
    assert layer.variable == "t2m"
    assert layer.visible is True


def test_data_renderer_constructs_and_initializes_without_crashing():
    dr = DataRenderer()
    fig, ax = dr.initialize_map()
    assert fig is not None
    assert ax is not None


def test_data_renderer_find_and_create_layer():
    dr = DataRenderer()
    ds = _sample_dataset()

    layer = dr.create_layer(ds, "t2m")
    assert layer.variable == "t2m"

    with pytest.raises(ValueError):
        dr.create_layer(ds, "no_such_variable_anywhere")


def test_data_renderer_render_produces_a_real_contour_layer():
    dr = DataRenderer()
    dr.initialize_map()
    lon = np.linspace(-10.0, 10.0, 5)
    lat = np.linspace(30.0, 40.0, 5)
    data = np.random.default_rng(0).random((5, 5))

    layer = dr.render(lon, lat, data, "temperature")
    assert layer is not None
    status = dr.status()
    assert status["cartopy"]["layers"] == 1


def test_auto_renderer_detects_variable_family_and_renders():
    auto = AutoRenderer()
    auto.initialize()
    ds = _sample_dataset()
    lon = np.linspace(-10.0, 10.0, 3)
    lat = np.linspace(30.0, 40.0, 3)
    data = np.random.default_rng(0).random((3, 3))

    variable = auto.render_dataset(ds, "temperature", lon, lat, data)
    assert variable == "t2m"

    with pytest.raises(ValueError):
        auto.render_dataset(ds, "wind", lon, lat, data)  # no wind-family variable in ds


def test_visualization_manager_full_render_round_trip():
    vm = VisualizationManager()
    vm.initialize()

    ds = _sample_dataset()
    vm.load_dataset(ds)

    lon = np.linspace(-10.0, 10.0, 4)
    lat = np.linspace(30.0, 40.0, 4)
    data = np.random.default_rng(0).random((4, 4))

    layer = vm.render("temperature", lon, lat, data)
    assert layer is not None

    status = vm.status()
    assert status["dataset"] == "test_ds"
    assert status["layer_manager"]["layers"] == 1

    vm.remove_layer(layer.id)
    assert vm.status()["layer_manager"]["layers"] == 0

    vm.clear()
    assert vm.dataset() is None
