"""
Tests for acf.storage - the Storage layer (docs/
ACF_ARCHITECTURE_TARGET_GAP_MAP.md, explicit user request "vas-y,
construis storage/").
"""

import csv

import numpy as np
import pytest
import xarray as xr

from acf.storage import StorageWriter


def _sample_state():
    lats = np.array([10.0, 20.0, 30.0])
    lons = np.array([0.0, 5.0])
    levels = np.array([1000.0, 850.0])
    state = {
        "T": np.random.default_rng(0).uniform(260.0, 300.0, size=(2, 3, 2)),  # (level, lat, lon)
        "MSL": np.random.default_rng(1).uniform(98000.0, 103000.0, size=(3, 2)),  # (lat, lon)
    }
    return state, lats, lons, levels


def test_write_netcdf_produces_a_real_readable_file(tmp_path):
    state, lats, lons, levels = _sample_state()
    path = str(tmp_path / "out.nc")

    result_path = StorageWriter(path).write(state, lats, lons, levels=levels, format="netcdf")

    assert result_path == path
    ds = xr.open_dataset(path)
    assert "T" in ds.data_vars
    assert "MSL" in ds.data_vars
    assert ds.sizes["latitude"] == 3
    assert ds.sizes["longitude"] == 2
    np.testing.assert_allclose(ds["MSL"].values, state["MSL"])


def test_write_zarr_produces_a_real_store(tmp_path):
    state, lats, lons, levels = _sample_state()
    path = str(tmp_path / "out.zarr")

    result_path = StorageWriter(path).write(state, lats, lons, levels=levels, format="zarr")

    assert result_path == path
    ds = xr.open_zarr(path)
    assert "T" in ds.data_vars
    np.testing.assert_allclose(ds["T"].values, state["T"])


def test_write_csv_produces_the_real_long_format_table(tmp_path):
    state, lats, lons, levels = _sample_state()
    path = str(tmp_path / "out.csv")

    result_path = StorageWriter(path).write(state, lats, lons, levels=levels, format="csv")
    assert result_path == path

    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # T is (2 levels, 3 lats, 2 lons) = 12 rows; MSL is (3 lats, 2 lons) = 6 rows.
    t_rows = [r for r in rows if r["variable"] == "T"]
    msl_rows = [r for r in rows if r["variable"] == "MSL"]
    assert len(t_rows) == 12
    assert len(msl_rows) == 6
    # 2D variable rows must have an empty level, not a fabricated 0.
    assert all(r["level"] == "" for r in msl_rows)
    assert all(r["level"] != "" for r in t_rows)

    # Spot-check one real value round-trips exactly.
    first_t = t_rows[0]
    assert float(first_t["value"]) == pytest.approx(state["T"][0, 0, 0])


def test_write_unknown_format_raises_not_falls_back(tmp_path):
    state, lats, lons, levels = _sample_state()
    with pytest.raises(ValueError, match="Unknown format"):
        StorageWriter(str(tmp_path / "out.xyz")).write(state, lats, lons, levels=levels, format="geotiff")


def test_write_csv_2d_only_state(tmp_path):
    """A state with only 2D variables must not require `levels` at all."""
    lats = np.array([0.0, 1.0])
    lons = np.array([0.0, 1.0])
    state = {"SST": np.array([[290.0, 291.0], [292.0, 293.0]])}
    path = str(tmp_path / "sst.csv")

    StorageWriter(path).write(state, lats, lons, levels=None, format="csv")

    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4
    assert all(r["level"] == "" for r in rows)
