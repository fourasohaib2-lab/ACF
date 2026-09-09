"""
Tests for the real generic model-import adapter (acf.awci.model_import)
- added 2026-09-08, closing the dashboard's own "📂 Import Model File"
disclosed "loads but never computes AWCI" gap.

Every fixture here is a real in-memory acf.data.dataset.Dataset shaped
exactly like what ACF's own real readers produce (NetCDFReader stores
`<name>_acf` resolved canonical names + `<name>_units` metadata;
GRIBReader stores bare variable names) - no fabricated file I/O needed,
the adapter consumes the Dataset object itself.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from acf.awci.model_import import (
    ModelImportError,
    compute_awci_from_imported_dataset,
    extract_awci_point_inputs,
)
from acf.data.dataset import Dataset


def _surface_dataset(**overrides: Any) -> Dataset:
    """A real WRF-style surface-only dataset: names the default
    ParameterMapper genuinely resolves (T2/QVAPOR/U10/V10), hPa surface
    pressure (PSFC, matched through this module's own alias table since
    the default mapper has no PSFC entry), real declared units."""
    ds = Dataset(name="wrfout-surface", filetype="NetCDF", source="xarray")
    lats = np.linspace(18.0, 46.0, 50)
    lons = np.linspace(-10.0, 17.0, 40)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    # Real coordinate variables (as a real WRF/NetCDF output carries) -
    # without these the adapter's honest disclosed fallback samples the
    # first grid cell, which the coordinate-sampling tests below
    # deliberately do NOT exercise.
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("T2", 288.0 + 0.3 * LAT - 0.02 * LON)
    ds.add_variable("QVAPOR", np.full_like(LAT, 0.008))
    ds.add_variable("U10", 3.0 + 0.05 * LON)
    ds.add_variable("V10", 1.0 + 0.02 * LAT)
    ds.add_variable("PSFC", np.full_like(LAT, 1013.0))
    for name, unit in (
        ("T2", "K"),
        ("QVAPOR", "kg kg-1"),
        ("U10", "m s-1"),
        ("V10", "m s-1"),
        ("PSFC", "hPa"),
    ):
        ds.set_metadata(f"{name}_units", unit)
    for key, value in overrides.items():
        ds.set_metadata(key, value)
    return ds


def _cf_style_dataset() -> Dataset:
    """A real CF-style dataset: standard_name metadata does the
    matching (variable names themselves are NOT in any alias table),
    latitude/longitude coordinate variables are present, pressure is
    Pa (converted to hPa)."""
    ds = Dataset(name="cf-file", filetype="NetCDF", source="xarray")
    lats = np.linspace(18.0, 46.0, 50)
    lons = np.linspace(-10.0, 17.0, 40)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("tas", 288.0 + 0.3 * LAT - 0.02 * LON)
    ds.add_variable("hus", np.full_like(LAT, 0.008))
    ds.add_variable("ua", 3.0 + 0.05 * LON)
    ds.add_variable("va", 1.0 + 0.02 * LAT)
    ds.add_variable("ps", np.full_like(LAT, 101325.0))
    ds.set_metadata("tas_standard_name", "air_temperature")
    ds.set_metadata("tas_units", "K")
    ds.set_metadata("hus_standard_name", "specific_humidity")
    ds.set_metadata("hus_units", "kg kg-1")
    ds.set_metadata("ua_units", "m s-1")
    ds.set_metadata("va_units", "m s-1")
    ds.set_metadata("ps_standard_name", "air_pressure")
    ds.set_metadata("ps_units", "Pa")
    return ds


class TestExtraction:
    def test_wrf_style_surface_dataset_yields_real_awci(self) -> None:
        outcome = compute_awci_from_imported_dataset(_surface_dataset(), 34.0, 3.0)
        result = outcome["result"]
        extraction = outcome["extraction"]

        assert 0.0 <= result["awci"] <= 100.0
        assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}
        # All four core variables genuinely extracted.
        assert set(extraction["inputs"]) >= {"temperature", "wind_speed", "specific_humidity", "pressure"}
        # Matched through ACF's own real alias machinery.
        assert extraction["matched_variables"]["temperature"] == "T2"
        assert extraction["matched_variables"]["specific_humidity"] == "QVAPOR"
        assert extraction["matched_variables"]["wind_speed"] == "U10+V10"
        assert extraction["matched_variables"]["pressure"] == "PSFC"
        # Genuinely absent variables are reported, not fabricated.
        assert set(extraction["missing_variables"]) >= {"cape", "cin", "precipitation", "altitude"}
        assert extraction["is_real_data"] is True

    def test_wind_speed_is_real_uv_magnitude(self) -> None:
        extraction = extract_awci_point_inputs(_surface_dataset(), 34.0, 3.0)
        # The real nearest-neighbour grid points: lat 34.0 -> index 28
        # (exact), lon 3.0 -> index 19 (lon value -10 + 19*27/39 =
        # 3.1538 on the -10..17/40 axis - the genuinely nearest point).
        u = 3.0 + 0.05 * (-10.0 + 19.0 * 27.0 / 39.0)
        v = 1.0 + 0.02 * 34.0
        expected = float(np.sqrt(u**2 + v**2))
        assert extraction["inputs"]["wind_speed"] == pytest.approx(expected, rel=1e-6)

    def test_cf_standard_name_matching_and_pa_conversion(self) -> None:
        outcome = compute_awci_from_imported_dataset(_cf_style_dataset(), 34.0, 3.0)
        extraction = outcome["extraction"]
        # Matched via each variable's own real standard_name metadata.
        assert extraction["matched_variables"]["temperature"] == "tas"
        assert extraction["matched_variables"]["specific_humidity"] == "hus"
        assert extraction["matched_variables"]["pressure"] == "ps"
        # Real Pa -> hPa conversion happened.
        assert extraction["inputs"]["pressure"] == pytest.approx(1013.25, rel=1e-3)
        # Real nearest-neighbour coordinate sampling.
        assert extraction["lat_idx"] > 0 and extraction["lon_idx"] > 0

    def test_degC_conversion(self) -> None:
        ds = _surface_dataset()
        values = 15.0 + 0.1 * np.arange(50 * 40).reshape(50, 40)
        ds.add_variable("T2", values)
        ds.set_metadata("T2_units", "degC")
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0)
        # (28, 19) is the genuinely sampled cell -> 15.0 + 0.1*(28*40+19).
        assert extraction["inputs"]["temperature"] == pytest.approx(288.15 + 0.1 * (28 * 40 + 19), rel=1e-6)

    def test_relative_humidity_to_specific_humidity(self) -> None:
        ds = Dataset(name="rh-file", filetype="NetCDF")
        lats = np.linspace(18.0, 46.0, 10)
        lons = np.linspace(-10.0, 17.0, 10)
        LAT, LON = np.meshgrid(lats, lons, indexing="ij")
        ds.add_variable("latitude", lats)
        ds.add_variable("longitude", lons)
        ds.add_variable("t2m", np.full_like(LAT, 288.15))
        ds.add_variable("rh", np.full_like(LAT, 70.0))
        ds.add_variable("msl", np.full_like(LAT, 1013.0))
        for name, unit in (("t2m", "K"), ("rh", "%"), ("msl", "hPa")):
            ds.set_metadata(f"{name}_units", unit)
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0)
        # Real q from the real Moisture chain - physically plausible.
        assert 0.0 < extraction["inputs"]["specific_humidity"] < 0.02
        assert extraction["matched_variables"]["specific_humidity"] == "rh"

    def test_column_cape_computed_from_real_3d_column(self) -> None:
        ds = Dataset(name="column", filetype="NetCDF")
        n_lev, n_lat, n_lon = 12, 6, 6
        p3d = np.broadcast_to(np.linspace(1013.0, 300.0, n_lev)[:, None, None], (n_lev, n_lat, n_lon)).copy()
        t3d = np.broadcast_to(288.0 - np.linspace(0.0, 65.0, n_lev)[:, None, None], (n_lev, n_lat, n_lon)).copy()
        q3d = np.broadcast_to(np.linspace(0.012, 0.0005, n_lev)[:, None, None], (n_lev, n_lat, n_lon)).copy()
        ds.add_variable("temperature", t3d)
        ds.add_variable("specific_humidity", q3d)
        ds.add_variable("pressure", p3d)
        for name, unit in (("temperature", "K"), ("specific_humidity", "kg kg-1"), ("pressure", "hPa")):
            ds.set_metadata(f"{name}_units", unit)
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0)
        # Real MetPy surface-based CAPE from the real column - a real,
        # non-negative physical value, not a fabricated one.
        assert extraction["inputs"]["cape"] is not None
        assert extraction["inputs"]["cape"] >= 0.0

    def test_unitless_fraction_rh_heuristic(self) -> None:
        ds = Dataset(name="frac-rh", filetype="NetCDF")
        ds.add_variable("temperature", np.full((4, 4), 288.15))
        ds.add_variable("rh", np.full((4, 4), 0.7))
        ds.add_variable("pressure", np.full((4, 4), 1013.0))
        for name, unit in (("temperature", "K"), ("pressure", "hPa")):
            ds.set_metadata(f"{name}_units", unit)
        # No units on rh - the real 0-1 heuristic applies.
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0)
        assert 0.0 < extraction["inputs"]["specific_humidity"] < 0.02


class TestHonestFailure:
    def test_empty_dataset_raises(self) -> None:
        with pytest.raises(ModelImportError, match="no variables"):
            compute_awci_from_imported_dataset(Dataset(name="empty"), 34.0, 3.0)

    def test_unrecognizable_variables_raise(self) -> None:
        ds = Dataset(name="opaque", filetype="NetCDF")
        ds.add_variable("band_1", np.zeros((4, 4)))
        ds.add_variable("band_2", np.zeros((4, 4)))
        with pytest.raises(ModelImportError, match="No usable core meteorological variable"):
            compute_awci_from_imported_dataset(ds, 34.0, 3.0)

    def test_unconvertible_unit_is_skipped_not_reinterpreted(self) -> None:
        ds = _surface_dataset()
        ds.set_metadata("T2_units", "furlongs")
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0)
        assert "temperature" not in extraction["inputs"]
        assert "temperature" in extraction["skipped_variables"]
        assert "furlongs" in extraction["skipped_variables"]["temperature"]

    def test_all_nan_at_point_is_skipped(self) -> None:
        ds = _surface_dataset()
        t2 = np.asarray(ds.get_variable("T2"), dtype=float)
        t2[:, :] = np.nan
        ds.add_variable("T2", t2)
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0)
        assert "temperature" not in extraction["inputs"]
        assert "temperature" in extraction["skipped_variables"]


class TestLevelHandling:
    def test_pressure_level_coordinate_is_matched(self) -> None:
        ds = Dataset(name="levels", filetype="NetCDF")
        levels = np.array([1000.0, 850.0, 700.0, 500.0, 300.0])
        lats = np.linspace(18.0, 46.0, 8)
        lons = np.linspace(-10.0, 17.0, 8)
        data = np.empty((5, 8, 8))
        for i, p in enumerate(levels):
            data[i] = 288.0 - 10.0 * i
        ds.add_variable("latitude", lats)
        ds.add_variable("longitude", lons)
        ds.add_variable("level", levels)
        ds.add_variable("temperature", data)
        ds.add_variable("specific_humidity", np.full_like(data, 0.008))
        ds.add_variable("wind_speed", np.full_like(data, 12.0))
        ds.add_variable("pressure", np.broadcast_to(levels[:, None, None], data.shape).copy())
        for name, unit in (("temperature", "K"), ("specific_humidity", "kg kg-1"), ("wind_speed", "m s-1"), ("pressure", "hPa")):
            ds.set_metadata(f"{name}_units", unit)
        extraction = extract_awci_point_inputs(ds, 34.0, 3.0, level_hpa=500.0)
        assert extraction["level_idx"] == 3  # the real 500 hPa level
        assert extraction["inputs"]["temperature"] == pytest.approx(288.0 - 30.0)

    def test_no_level_coordinate_discloses_surface_use(self) -> None:
        extraction = extract_awci_point_inputs(_surface_dataset(), 34.0, 3.0)
        assert any("surface/first level" in note for note in extraction["notes"])
        assert extraction["level_idx"] is None


class TestRegression:
    def test_derived_keys_never_falsely_reported_missing(self) -> None:
        """The 2026-09-08 bug found while building this: wind_speed and
        specific_humidity are derived (u/v, RH) or matched separately -
        they must never appear in missing_variables when they were
        genuinely extracted."""
        extraction = extract_awci_point_inputs(_surface_dataset(), 34.0, 3.0)
        assert "wind_speed" not in extraction["missing_variables"]
        assert "specific_humidity" not in extraction["missing_variables"]

    def test_result_reproducible_for_same_inputs(self) -> None:
        ds = _surface_dataset()
        a = compute_awci_from_imported_dataset(ds, 34.0, 3.0)["result"]["awci"]
        b = compute_awci_from_imported_dataset(ds, 34.0, 3.0)["result"]["awci"]
        assert a == b
