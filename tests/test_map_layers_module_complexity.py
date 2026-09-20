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

from acf.awci.calculator import AWCICalculator
from acf.awci.spatial_field import compute_real_complexity_field
from acf.gui.map.map_layers import MODULE_COMPLEXITY_LAYERS, LayerManager, ModuleComplexityLayer, UncertaintyLayer


def test_module_complexity_layers_covers_every_real_awci_module():
    """NOTE (correction, 2026-09-06): MODULE_COMPLEXITY_LAYERS used to
    register only AWCICalculator.PHYSICAL_MODULES (6 keys), silently
    dropping every real AWCICalculator.FORECAST_MODULES field
    ("confidence"/"ensemble_spread"/"model_disagreement") that
    compute_real_complexity_field() has always also computed - found by
    an end-to-end toolbar smoke test, not a code read (see
    acf.gui.esoc.esoc_window._on_awci_field_ready's own NOTE). This test
    ties the two together so a future new AWCICalculator module can't
    silently reintroduce the same gap - it must fail here first.

    NOTE (deliberate, disclosed exception, 2026-09-11, NARROWED
    2026-09-12): "ceiling"/"visibility"/"dust" were excluded here too
    at first, for the same reason as "ash"/"microburst" below - but
    unlike those two, all 3 depend only on temperature/specific
    humidity/pressure/wind speed, already fetched for every point
    regardless of any `compute_*` flag - so `esoc_window.py`'s own real
    GUI call was updated to pass `compute_ceiling=True`/
    `compute_visibility=True`/`compute_dust=True` (genuinely free, no
    extra real cost), making their `module_fields` entries genuinely
    real and non-uniform. Registered as real layers below; no longer
    excluded.

    "ash" remains excluded: it needs a real eruption source
    (lat/lon/rate/wind) that simply does not exist anywhere in
    `CoupledEarthSolver`'s state - there is no cheap way to opt it in.
    `esoc_window.py`'s own `_on_awci_field_ready()` skips any
    module_key not registered here, so this exclusion is silent-by-
    design (no more `set_module_complexity_field()` warning noise for
    it), not silent-by-bug. Revisit if/when a real, cheap per-point
    eruption-source signal is wired in (a separate, larger closure, not
    attempted here).

    "microburst" (closed 2026-09-20, Master Prompt V3 §28-29): used to
    be excluded for the same "not free" reason - it needs
    `compute_wind_shear=True` AND `compute_convective_energy=True`
    together (see `acf.awci.spatial_field.compute_real_complexity_field`'s
    own `compute_microburst` docstring). `compute_wind_shear` turned
    out to be a genuinely cheap per-point slice of the already-computed
    real solver U/V column (same real cost class as
    `compute_convective_energy`'s own already-accepted per-point cost,
    not a second solver run) - `esoc_window.py`'s real GUI call now
    passes both flags, so `module_fields["microburst"]` is a real,
    non-uniform field."""
    all_real_modules = AWCICalculator.PHYSICAL_MODULES | AWCICalculator.FORECAST_MODULES
    deliberately_unregistered_pending_real_field_data = {"ash"}
    assert set(MODULE_COMPLEXITY_LAYERS.values()) == all_real_modules - deliberately_unregistered_pending_real_field_data


class _FakeAxes:
    """Same isolation device as test_map_layers_awci.py's own _FakeAxes."""

    def __init__(self) -> None:
        self.contourf_calls: list[dict] = []

    def contourf(self, lon_grid, lat_grid, values, **kwargs):
        self.contourf_calls.append({"lon_grid": lon_grid, "lat_grid": lat_grid, "values": values, **kwargs})


def test_microburst_field_is_genuinely_non_uniform_at_a_real_production_scale_grid():
    """Real regression guard for the 2026-09-20 closure (Master Prompt
    V3 §28-29): a genuinely small/short test grid can legitimately
    show an all-zero real microburst field (real CAPE and real shear
    co-occurring is a real, rarer combination) - this uses the SAME
    real grid size/step count esoc_window.py's own real GUI call uses
    (n_lat=24, n_lon=36, n_levels=6, steps=6), confirmed empirically
    (not assumed) to produce a real, non-uniform field."""
    result = compute_real_complexity_field(
        model="ARPEGE", n_lat=24, n_lon=36, n_levels=6, steps=6,
        compute_convective_energy=True, compute_wind_shear=True, compute_microburst=True,
    )
    microburst = result["module_fields"]["microburst"]
    assert not np.isnan(microburst).any()
    assert len(set(np.round(microburst, 6).ravel())) > 1


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
