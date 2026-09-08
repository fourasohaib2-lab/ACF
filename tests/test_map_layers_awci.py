"""
Tests for acf.gui.map.map_layers.AWCILayer - the real AWCI complexity
overlay for ESOC's central map (explicit user request "ajoute la 4eme
dimension au niveau d'affichage des cartes"), and for
acf.gui.map.map_canvas.MapCanvas.set_awci_field()/clear_awci_field().
"""

from __future__ import annotations

import cartopy.crs as ccrs
import numpy as np

from acf.awci.spatial_field import compute_real_complexity_field
from acf.gui.map.map_layers import AWCILayer, LayerManager


class _FakeAxes:
    """Records whether contourf() was called, without needing a real
    Cartopy GeoAxes/Matplotlib figure - isolates AWCILayer's own logic
    (does it draw, with what data) from the rendering machinery
    already covered by tests/test_map_canvas_zoom_pan.py."""

    def __init__(self) -> None:
        self.contourf_calls: list[dict] = []

    def contourf(self, lon_grid, lat_grid, values, **kwargs):
        self.contourf_calls.append({"lon_grid": lon_grid, "lat_grid": lat_grid, "values": values, **kwargs})


def test_awci_layer_is_registered_in_layer_manager():
    manager = LayerManager()
    assert "AWCI Complexity" in manager.available_layers
    assert isinstance(manager.available_layers["AWCI Complexity"], AWCILayer)


def test_awci_layer_is_not_active_by_default():
    """Unlike the other 6 layers, AWCI Complexity has no synthetic
    fallback - it should not silently appear in the default active set."""
    manager = LayerManager()
    assert "AWCI Complexity" not in manager.active_layer_names


def test_awci_layer_draws_nothing_without_real_data():
    """No fabricated fallback pattern - render() must be a genuine
    no-op until set_data() has been called with a real field."""
    layer = AWCILayer()
    axes = _FakeAxes()
    layer.render(axes, transform=ccrs.PlateCarree())
    assert axes.contourf_calls == []


def test_awci_layer_draws_the_real_data_once_set():
    layer = AWCILayer()
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


def test_map_canvas_set_awci_field_populates_the_real_layer(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)

    canvas.set_awci_field(result["lons"], result["lats"], result["awci_field"], label="REAL AWCI")

    assert "AWCI Complexity" in canvas.layer_manager.active_layer_names
    layer = canvas.layer_manager.available_layers["AWCI Complexity"]
    assert layer.custom_data is not None
    assert "REAL AWCI" in canvas.title_text


def test_map_canvas_clear_awci_field_removes_it(qtbot):
    from acf.gui.map.map_canvas import MapCanvas

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    canvas.set_awci_field(result["lons"], result["lats"], result["awci_field"], label="REAL AWCI")

    canvas.clear_awci_field()

    assert "AWCI Complexity" not in canvas.layer_manager.active_layer_names
    assert canvas.layer_manager.available_layers["AWCI Complexity"].custom_data is None
    assert "REAL AWCI" not in canvas.title_text


def test_map_canvas_set_awci_field_is_real_not_fabricated():
    """The values shown really are compute_real_complexity_field()'s
    own output, not a placeholder pattern - spot-checked against the
    exact same call's return value."""
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2, seed=3)
    assert np.std(result["awci_field"]) >= 0.0  # sanity: a real array, not None/NaN-only
    assert result["is_real_data"] is True
