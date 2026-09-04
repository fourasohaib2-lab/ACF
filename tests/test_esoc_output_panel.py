"""
Tests for acf.gui.esoc.panel_manager.OutputPanel - the real NetCDF4/
Zarr/GeoTIFF export panel closing the previously-empty "Output" System
Explorer category (2026-09-04, fifth of 7 ESOC categories with no
real panel).
"""

from __future__ import annotations

import pytest
import xarray as xr
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import OutputPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_output_panel_shows_the_real_export_directory(qapp, registry, tmp_path):
    dispatcher = CommandDispatcher()

    panel = OutputPanel(registry, dispatcher, export_dir=tmp_path)

    assert panel._export_dir == tmp_path
    assert panel.status_label.text() == "No real export run yet."


def test_netcdf_export_writes_a_real_readable_file_with_every_real_variable(qapp, registry, tmp_path):
    dispatcher = CommandDispatcher()
    panel = OutputPanel(registry, dispatcher, export_dir=tmp_path)

    panel.netcdf_button.click()

    path = tmp_path / "coupled_state.nc"
    assert path.exists()
    assert "✅" in panel.status_label.text()
    with xr.open_dataset(path) as ds:
        expected = registry.get_module("coupled_earth_solver").initialize_coupled_state()
        assert set(ds.data_vars) == set(expected)
        assert ds.sizes["level"] == registry.get_module("coupled_earth_solver").grid.n_levels
        assert ds.sizes["step"] == expected["Soil"].shape[0]


def test_zarr_export_writes_a_real_readable_store_with_every_real_variable(qapp, registry, tmp_path):
    dispatcher = CommandDispatcher()
    panel = OutputPanel(registry, dispatcher, export_dir=tmp_path)

    panel.zarr_button.click()

    path = tmp_path / "coupled_state.zarr"
    assert path.exists()
    assert "✅" in panel.status_label.text()
    ds = xr.open_zarr(path)
    expected = registry.get_module("coupled_earth_solver").initialize_coupled_state()
    assert set(ds.data_vars) == set(expected)


def test_geotiff_export_writes_a_real_readable_raster_matching_the_real_surface_temperature(qapp, registry, tmp_path):
    rasterio = pytest.importorskip("rasterio")
    import numpy as np

    dispatcher = CommandDispatcher()
    panel = OutputPanel(registry, dispatcher, export_dir=tmp_path)

    panel.geotiff_button.click()

    path = tmp_path / "surface_temperature.tif"
    assert path.exists()
    assert "✅" in panel.status_label.text()
    expected = registry.get_module("coupled_earth_solver").initialize_coupled_state()["T"][0]
    with rasterio.open(path) as src:
        assert str(src.crs) == "EPSG:4326"
        readback = src.read(1)
        np.testing.assert_allclose(np.flipud(readback), expected)


def test_output_panel_honestly_discloses_grib2_is_not_available(qapp, registry, tmp_path):
    dispatcher = CommandDispatcher()

    panel = OutputPanel(registry, dispatcher, export_dir=tmp_path)

    assert "GRIB2" in panel.grib_label.text()
    assert "not available" in panel.grib_label.text()
    assert not hasattr(panel, "grib_button")


def test_output_panel_honestly_discloses_when_the_real_solver_is_not_connected(qapp, tmp_path):
    class _EmptyRegistry:
        def get_module(self, name: str):
            return None

    dispatcher = CommandDispatcher()
    panel = OutputPanel(_EmptyRegistry(), dispatcher, export_dir=tmp_path)  # type: ignore[arg-type]

    assert not hasattr(panel, "netcdf_button")
