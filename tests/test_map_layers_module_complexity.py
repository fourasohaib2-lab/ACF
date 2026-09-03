"""
Tests for acf.gui.map.map_layers.ModuleComplexityLayer/UncertaintyLayer
- real per-module complexity map layers (docs/ACF_MASTER_PROMPT.md
sections 28-29: "Dynamic complexity, Thermodynamic complexity,
Convective complexity, Microphysical complexity, Orographic
complexity, Temporal complexity, Uncertainty" as separate toggleable
layers, distinct from the single combined "AWCI Complexity" layer),
and for acf.gui.map.map_canvas.MapCanvas.set_module_complexity_field()/
clear_module_complexity_field()/set_uncertainty_field()/
clear_uncertainty_field(). Same real-data-only discipline as
tests/test_map_layers_awci.py.
"""

from __future__ import annotations

import cartopy.crs as ccrs
import numpy as np

from acf.awci.spatial_field import compute_real_complexity_field
from acf.gui.map.map_layers import MODULE_COMPLEXITY_LAYERS, LayerManager, ModuleComplexityLayer, UncertaintyLayer


class _FakeAxes:
    """Same isolation device as test_map_layers_awci.py's own _FakeAxes."""

    def __init__(self) -> None:
        self.contourf_calls: list[dict] = []

    def contourf(self, lon_grid, lat_grid, values, **kwargs):
        self.contourf_calls.append({"lon_grid": lon_grid, "lat_grid": lat_grid, "values": values, **kwargs})


def test_every_module_complexity_layer_is_registered():
    manager = LayerManager()
    for layer_name, module_key in MODULE_COMPLEXITY_LAYERS.items():
        assert layer_name in manager.available_layers
        layer = manager.available_layers[layer_name]
        assert isinstance(layer, ModuleComplexityLayer)
        assert layer.module_key == module_key


def test_uncertainty_layer_is_registered():
    manager = LayerManager()
    assert "Uncertainty" in manager.available_layers
    assert isinstance(manager.available_layers["Uncertainty"], UncertaintyLayer)


def test_none_of_the_new_layers_are_active_by_default():
    manager = LayerManager()
    for layer_name in (*MODULE_COMPLEXITY_LAYERS, "Uncertainty"):
        assert layer_name not in manager.active_layer_names


def test_module_complexity_layer_draws_nothing_without_real_data():
    layer = ModuleComplexityLayer("Dynamic Complexity", "dynamic", zorder=17)
    axes = _FakeAxes()
    layer.render(axes, transform=ccrs.PlateCarree())
    assert axes.contourf_calls == []


def test_module_complexity_layer_draws_the_real_data_once_set():
    layer = ModuleComplexityLayer("Dynamic Complexity", "dynamic", zorder=17)
    lons = np.linspace(-10, 10, 5)
    lats = np.linspace(-5, 5, 4)
    values = np.random.default_rng(0).uniform(0, 100, size=(4, 5))
    layer.set_data(lons, lats, values)

    axes = _FakeAxes()
    layer.render(axes, transform=ccrs.PlateCarree())

    assert len(axes.contourf_calls) == 1
    call = axes.contourf_calls[0]
    assert call["vmin"] == 0
    assert call["vmax"] == 100
    assert np.array_equal(call["values"], values)


def test_uncertainty_layer_draws_the_real_data_once_set():
    layer = UncertaintyLayer()
    lons = np.linspace(-10, 10, 5)
    lats = np.linspace(-5, 5, 4)
    values = np.random.default_rng(0).uniform(0, 100, size=(4, 5))
    layer.set_data(lons, lats, values)

    axes = _FakeAxes()
    layer.render(axes, transform=ccrs.PlateCarree())

    assert len(axes.contourf_calls) == 1
    assert np.array_equal(axes.contourf_calls[0]["values"], values)


def test_map_canvas_set_module_complexity_field_populates_the_real_layer(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)

    canvas.set_module_complexity_field(
        "dynamic", result["lons"], result["lats"], result["module_fields"]["dynamic"], label="t+0h"
    )

    assert "Dynamic Complexity" in canvas.layer_manager.active_layer_names
    layer = canvas.layer_manager.available_layers["Dynamic Complexity"]
    assert layer.custom_data is not None
    assert np.array_equal(layer.custom_data["values"], result["module_fields"]["dynamic"])
    assert "Dynamic Complexity" in canvas.title_text


def test_map_canvas_set_module_complexity_field_rejects_an_unknown_module_key(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    active_before = list(canvas.layer_manager.active_layer_names)

    canvas.set_module_complexity_field("not_a_real_module", [0.0], [0.0], np.zeros((1, 1)))

    assert canvas.layer_manager.active_layer_names == active_before
    for layer_name in MODULE_COMPLEXITY_LAYERS:
        assert layer_name not in canvas.layer_manager.active_layer_names


def test_map_canvas_clear_module_complexity_field_removes_it(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    canvas.set_module_complexity_field("dynamic", result["lons"], result["lats"], result["module_fields"]["dynamic"])

    canvas.clear_module_complexity_field("dynamic")

    assert "Dynamic Complexity" not in canvas.layer_manager.active_layer_names
    assert canvas.layer_manager.available_layers["Dynamic Complexity"].custom_data is None


def test_map_canvas_two_different_module_layers_are_independent(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)

    canvas.set_module_complexity_field("dynamic", result["lons"], result["lats"], result["module_fields"]["dynamic"])
    canvas.set_module_complexity_field(
        "thermodynamic", result["lons"], result["lats"], result["module_fields"]["thermodynamic"]
    )

    assert "Dynamic Complexity" in canvas.layer_manager.active_layer_names
    assert "Thermodynamic Complexity" in canvas.layer_manager.active_layer_names
    assert canvas.layer_manager.available_layers["Dynamic Complexity"].custom_data is not None
    assert canvas.layer_manager.available_layers["Thermodynamic Complexity"].custom_data is not None

    canvas.clear_module_complexity_field("dynamic")

    assert "Dynamic Complexity" not in canvas.layer_manager.active_layer_names
    # Clearing one module layer must not affect the other.
    assert "Thermodynamic Complexity" in canvas.layer_manager.active_layer_names
    assert canvas.layer_manager.available_layers["Thermodynamic Complexity"].custom_data is not None


def test_map_canvas_set_uncertainty_field_populates_the_real_layer(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)

    canvas.set_uncertainty_field(result["lons"], result["lats"], result["forecast_field"])

    assert "Uncertainty" in canvas.layer_manager.active_layer_names
    assert canvas.layer_manager.available_layers["Uncertainty"].custom_data is not None
    assert "Uncertainty" in canvas.title_text


def test_map_canvas_clear_uncertainty_field_removes_it(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    canvas.set_uncertainty_field(result["lons"], result["lats"], result["forecast_field"])

    canvas.clear_uncertainty_field()

    assert "Uncertainty" not in canvas.layer_manager.active_layer_names
    assert canvas.layer_manager.available_layers["Uncertainty"].custom_data is None
