"""
Tests for the generic 4D time-series import adapter
(acf.awci.model_import_evolution, added 2026-09-09) - closes the AWCI
completion report's disclosed "4D over imported data" gap: a file that
genuinely carries a time dimension becomes a real, per-grid-cell
AWCI(x, y, t) evolution feeding the SAME playback structure the solver
evolution already animates.

Every fixture is a real in-memory acf.data.dataset.Dataset shaped
exactly like what ACF's own real readers produce - no fabricated file
I/O, no fake values: every AWCI cell in the assertions is a genuine
AWCICalculator output over the fixture's own fields.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.model_import import ModelImportError
from acf.awci.model_import_evolution import compute_awci_evolution_from_imported_dataset
from acf.data.dataset import Dataset


def _evolution_dataset(n_time: int = 3) -> Dataset:
    """A real WRF-style time-series surface dataset (time, lat, lon)."""
    ds = Dataset(name="wrf-4d-test", filetype="NetCDF", source="xarray")
    lats = np.linspace(30.0, 40.0, 6)
    lons = np.linspace(0.0, 10.0, 8)
    T0 = 288.0 + 0.3 * (lats[:, None] - 30.0) - 0.02 * lons[None, :]
    for name, base, perturb, unit in (
        ("t2m", T0, 2.0, "K"),
        ("q", np.full_like(T0, 0.008), 0.0005, "kg kg-1"),
        ("u10", np.full_like(T0, 5.0), 1.5, "m s-1"),
        ("v10", np.full_like(T0, 1.0), 0.5, "m s-1"),
        ("sp", np.full_like(T0, 1013.0), 1.0, "hPa"),
    ):
        ds.add_variable(name, np.stack([base + k * perturb for k in range(n_time)], axis=0))
        ds.set_metadata(f"{name}_units", unit)
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("time", np.arange(n_time, dtype=float) * 6.0)
    ds.set_metadata("time_units", "hours since 2026-09-09 00:00:00")
    return ds


def test_time_series_file_produces_a_real_per_cell_evolution() -> None:
    ds = _evolution_dataset()

    out = compute_awci_evolution_from_imported_dataset(ds)

    ev = out["awci_evolution"]
    # Solver-evolution structure: (frames, 1, lat, lon).
    assert ev.shape == (3, 1, 6, 8)
    # Every cell is a REAL score in the real AWCI range - no NaN, no placeholder.
    assert np.isfinite(ev).all()
    assert float(ev.min()) >= 0.0 and float(ev.max()) <= 100.0
    assert out["status"] == "REAL_IMPORTED_MODEL_EVOLUTION"
    assert out["is_real_data"] is True


def test_evolution_genuinely_varies_across_real_valid_times() -> None:
    ds = _evolution_dataset()
    # Warming by 2 K per frame must change the real thermodynamic module
    # score -> the real AWCI field must differ between frames.
    out = compute_awci_evolution_from_imported_dataset(ds)
    ev = out["awci_evolution"]

    assert not np.allclose(ev[0], ev[2], equal_nan=True)


def test_valid_times_decoded_from_the_file_real_cf_time_units() -> None:
    ds = _evolution_dataset()
    out = compute_awci_evolution_from_imported_dataset(ds)

    # 0/6/12 in "hours since ..." -> real seconds.
    np.testing.assert_allclose(out["valid_time_seconds"], [0.0, 6 * 3600.0, 12 * 3600.0])


def test_time_coordinate_without_decodable_units_used_as_raw_seconds() -> None:
    ds = _evolution_dataset()
    ds.set_metadata("time_units", "not-a-real-cf-unit")
    out = compute_awci_evolution_from_imported_dataset(ds)

    np.testing.assert_allclose(out["valid_time_seconds"], [0.0, 6.0, 12.0])
    assert any("no decodable" in n for n in out["notes"])


def test_frame_indices_capped_uniformly_first_and_last_kept() -> None:
    ds = _evolution_dataset(n_time=10)

    out = compute_awci_evolution_from_imported_dataset(ds, n_frames_max=4)

    assert out["n_frames"] == 4
    assert out["frame_time_indices"] == [0, 3, 6, 9]
    assert out["awci_evolution"].shape[0] == 4


def test_static_surface_fields_held_constant_while_time_fields_move() -> None:
    """A 2-D (lat, lon) field has no time axis of its own - it is held
    constant across frames (disclosed real behaviour, not fabricated
    variation)."""
    ds = _evolution_dataset()
    orog = np.full((6, 8), 120.0)
    ds.add_variable("orog", orog)
    ds.set_metadata("orog_units", "m")

    out = compute_awci_evolution_from_imported_dataset(ds)

    # The evolution still genuinely moves (time fields move it) ...
    ev = out["awci_evolution"]
    assert not np.allclose(ev[0], ev[1], equal_nan=True)
    # ... and the file's own static field was matched, not dropped.
    assert any("orog" in v or "altitude" in v for v in out["matched_variables"])


def test_point_extraction_matches_a_real_single_time_slice() -> None:
    """Cross-check one cell against the per-point adapter on an
    equivalent single-time dataset - the 4D adapter's per-cell values
    are genuinely the same real calculation, not a parallel one."""
    from acf.awci.model_import import compute_awci_from_imported_dataset

    ds = _evolution_dataset()
    out = compute_awci_evolution_from_imported_dataset(ds, n_frames_max=1)

    single = Dataset(name="wrf-4d-single", filetype="NetCDF", source="xarray")
    for name in ds.variables:
        arr = np.asarray(ds.get_variable(name))
        if arr.ndim >= 3:
            single.add_variable(name, arr[0])
        else:
            single.add_variable(name, arr)
    for var_name in ds.variables:
        for suffix in ("_units", "_standard_name", "_long_name", "_acf"):
            meta = ds.get_metadata(f"{var_name}{suffix}")
            if meta is not None:
                single.set_metadata(f"{var_name}{suffix}", meta)

    point = compute_awci_from_imported_dataset(single, float(ds.get_variable("latitude")[3]), float(ds.get_variable("longitude")[4]))
    assert point["result"]["awci"] == pytest.approx(float(out["awci_evolution"][0, 0, 3, 4]), rel=1e-6)


def test_file_without_time_dimension_is_honestly_refused() -> None:
    ds = Dataset(name="static", filetype="NetCDF", source="xarray")
    lats = np.linspace(30.0, 40.0, 6)
    lons = np.linspace(0.0, 10.0, 8)
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("t2m", 288.0 + 0.3 * (lats[:, None] - 30.0))
    ds.set_metadata("t2m_units", "K")

    with pytest.raises(ModelImportError, match="time dimension"):
        compute_awci_evolution_from_imported_dataset(ds)


def test_file_without_coordinates_is_honestly_refused() -> None:
    ds = Dataset(name="opaque-4d", filetype="NetCDF", source="xarray")
    ds.add_variable("t2m", np.zeros((3, 4, 5)))

    with pytest.raises(ModelImportError, match="latitude/longitude"):
        compute_awci_evolution_from_imported_dataset(ds)


def test_file_without_core_variables_is_honestly_refused() -> None:
    ds = Dataset(name="no-core", filetype="NetCDF", source="xarray")
    lats = np.linspace(30.0, 40.0, 6)
    lons = np.linspace(0.0, 10.0, 8)
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("band_1", np.zeros((3, 6, 8)))

    with pytest.raises(ModelImportError, match="No usable core"):
        compute_awci_evolution_from_imported_dataset(ds)


def test_all_nan_frame_cells_stay_nan_not_zero() -> None:
    """A genuinely unextractable cell (ALL core fields NaN at that
    valid time) stays NaN - never coerced to 0 or a default AWCI. (A
    single NaN field alone would NOT produce NaN: the other real
    fields still extract and AWCICalculator's own default fills the
    missing one - the documented per-variable discipline.)"""
    ds = _evolution_dataset()
    for name in ("t2m", "q", "u10", "v10", "sp"):
        arr = np.asarray(ds.get_variable(name), dtype=float)
        arr[1, :, :] = np.nan  # whole second valid time unextractable
    out = compute_awci_evolution_from_imported_dataset(ds)

    ev = out["awci_evolution"]
    assert np.isnan(ev[1]).all()
    assert np.isfinite(ev[0]).all() and np.isfinite(ev[2]).all()
