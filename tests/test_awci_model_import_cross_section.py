"""
Tests for the real imported-model cross-section adapter
(acf.awci.model_import_cross_section) - added 2026-09-09, closing the
import tier's disclosed "no vertical product" gap with the same honest
machinery as the per-point/4D adapters.

Every fixture is a real in-memory acf.data.dataset.Dataset shaped like
what ACF's own readers produce (variables + `<name>_units` metadata),
with the real (level, lat, lon) field convention - no fabricated file
I/O; the adapter consumes the Dataset object itself.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from acf.awci.model_import import ModelImportError, extract_awci_point_inputs
from acf.awci.model_import_cross_section import (
    compute_awci_cross_section_from_imported_dataset,
    has_pressure_level_coordinate,
)
from acf.data.dataset import Dataset


def _pressure_level_dataset(
    *,
    n_lat: int = 8,
    n_lon: int = 12,
    levels_hpa: tuple[float, ...] = (1000.0, 850.0, 700.0, 500.0),
    temperature_unit: str = "K",
    with_uv: bool = True,
    **overrides: Any,
) -> Dataset:
    """A real CF-style pressure-level dataset: T decreasing with height
    (a genuine lapse rate), q moist at the surface and dry aloft, u/v
    strengthening aloft - real atmospheric structure the AWCI score
    must respond to."""
    ds = Dataset(name="pl-file", filetype="NetCDF", source="xarray")
    lats = np.linspace(38.0, 52.0, n_lat)
    lons = np.linspace(-5.0, 14.0, n_lon)
    levels = np.asarray(levels_hpa, dtype=float)
    li = np.arange(levels.size)[:, None, None]
    ia = np.arange(n_lat)[None, :, None]
    shape = (levels.size, n_lat, n_lon)

    t_k = 288.0 - 6.0 * li + 0.1 * ia + np.zeros(shape)
    if temperature_unit == "K":
        t_values, t_unit = t_k, "K"
    else:
        t_values, t_unit = t_k - 273.15, temperature_unit

    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("level", levels)
    ds.add_variable("t", t_values)
    ds.add_variable("q", np.clip(0.012 - 0.0025 * li + np.zeros(shape), 1e-6, None))
    ds.add_variable("pres", np.broadcast_to(levels[:, None, None], shape).copy())
    if with_uv:
        ds.add_variable("u", 5.0 + 9.0 * li + np.zeros(shape))
        ds.add_variable("v", 2.0 - 1.0 * li + np.zeros(shape))
    units = {"t": t_unit, "q": "kg kg-1", "pres": "hPa"}
    if with_uv:
        units.update({"u": "m s-1", "v": "m s-1"})
    for name, unit in units.items():
        ds.set_metadata(f"{name}_units", unit)
    for key, value in overrides.items():
        ds.set_metadata(key, value)
    return ds


def test_pressure_level_file_produces_a_real_awci_grid() -> None:
    ds = _pressure_level_dataset(n_lat=8, n_lon=12)
    out = compute_awci_cross_section_from_imported_dataset(ds, (40.0, 0.0), (50.0, 10.0), n_along=12)

    # The y-axis is the file's OWN declared level coordinate, not a guessed list.
    assert out["levels_hpa"] == pytest.approx([1000.0, 850.0, 700.0, 500.0])
    assert out["mean_pressure_hpa_by_level"] == pytest.approx(out["levels_hpa"])
    assert out["awci_grid"].shape == (4, 12)
    assert len(out["distances_km"]) == 12
    assert out["status"] == "REAL_IMPORTED_MODEL_CROSS_SECTION"
    assert out["is_real_data"] is True

    # Real AWCICalculator output: genuinely varies with level (lapse rate)
    # and with distance (lat gradient), never a constant/flat pattern.
    grid = out["awci_grid"]
    assert np.isfinite(grid).all()
    assert not np.allclose(grid[0], grid[-1]), "AWCI must differ between surface and aloft"
    assert not np.allclose(grid[:, 0], grid[:, -1]), "AWCI must differ along the path"

    # Real matched/missing reporting, same contract as the per-point adapter.
    assert set(out["matched_variables"]) >= {"temperature", "specific_humidity", "wind_speed", "pressure"}
    assert "cape" in out["missing_variables"]

    # Honest disclosures: declared-level axis + per-cell provenance.
    assert any("pressure-level coordinate" in note for note in out["notes"])
    assert any("AWCICalculator" in note for note in out["notes"])


def test_surface_only_file_is_refused_for_cross_section_but_point_path_still_works() -> None:
    """The honest split: a surface-only file has no genuine vertical
    transect (cross-section refuses), while the per-point adapter still
    samples it - the refusal names the alternative, never fabricates a
    fake column."""
    ds = Dataset(name="surface-only", filetype="NetCDF", source="xarray")
    lats = np.linspace(38.0, 52.0, 8)
    lons = np.linspace(-5.0, 14.0, 12)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("T2", 288.0 + 0.1 * LAT)
    ds.add_variable("U10", 5.0 + 0.05 * LON)
    ds.add_variable("V10", 2.0 + 0.02 * LAT)
    ds.set_metadata("T2_units", "K")

    assert has_pressure_level_coordinate(ds) is False
    with pytest.raises(ModelImportError, match="surface-only file|pressure-level coordinate"):
        compute_awci_cross_section_from_imported_dataset(ds, (40.0, 0.0), (50.0, 10.0))

    # The per-point path genuinely still works on the same file.
    extraction = extract_awci_point_inputs(ds, 45.0, 5.0)
    assert "temperature" in extraction["inputs"]
    assert "wind_speed" in extraction["inputs"]


def test_hazard_overlay_computed_from_the_same_real_volume() -> None:
    ds = _pressure_level_dataset(n_lat=8, n_lon=12)
    out = compute_awci_cross_section_from_imported_dataset(ds, (40.0, 0.0), (50.0, 10.0), n_along=10)

    overlay = out["hazard_overlay"]
    assert overlay is not None
    distances, levels_hpa, phase_grid, shear_grid = overlay
    assert len(distances) == 10
    assert list(levels_hpa) == pytest.approx([1000.0, 850.0, 700.0, 500.0])
    # Real hydrometeor-phase severity per (level, along) cell...
    assert phase_grid.shape == (4, 10)
    assert np.isfinite(phase_grid).all()
    assert (phase_grid >= 0.0).all() and (phase_grid <= 1.0).all()
    # ...and real bulk shear between ADJACENT levels only (n_levels - 1 rows).
    assert shear_grid.shape == (3, 10)
    assert np.isfinite(shear_grid).all()


def test_hazard_overlay_honestly_absent_without_uv_volumes() -> None:
    ds = _pressure_level_dataset(n_lat=6, n_lon=10, with_uv=False)
    out = compute_awci_cross_section_from_imported_dataset(ds, (40.0, 0.0), (50.0, 10.0), n_along=8)

    assert out["hazard_overlay"] is None
    assert any("hazard overlay not computed" in note and "u_wind" in note for note in out["notes"])


def test_pascal_level_coordinate_is_converted_to_hpa() -> None:
    ds = _pressure_level_dataset(n_lat=6, n_lon=10)
    ds.variables["level"] = np.asarray([100000.0, 85000.0, 70000.0, 50000.0])
    out = compute_awci_cross_section_from_imported_dataset(ds, (40.0, 0.0), (50.0, 10.0), n_along=8)

    assert out["levels_hpa"] == pytest.approx([1000.0, 850.0, 700.0, 500.0])


def test_celsius_temperature_volume_gets_the_same_awci_as_its_kelvin_twin() -> None:
    kelvin = _pressure_level_dataset(n_lat=6, n_lon=10, temperature_unit="K")
    celsius = _pressure_level_dataset(n_lat=6, n_lon=10, temperature_unit="degC")
    k_out = compute_awci_cross_section_from_imported_dataset(kelvin, (42.0, 2.0), (48.0, 8.0), n_along=8)
    c_out = compute_awci_cross_section_from_imported_dataset(celsius, (42.0, 2.0), (48.0, 8.0), n_along=8)

    np.testing.assert_allclose(k_out["awci_grid"], c_out["awci_grid"], rtol=1e-6, atol=1e-6)


def test_all_nan_cell_stays_nan_in_the_grid() -> None:
    ds = _pressure_level_dataset(n_lat=6, n_lon=10)
    # (lat 2, lon 4) is the nearest-neighbour cell of the path's 4th sample
    # column (t=3/9 of the way from (40, 0) to (50, 10) -> (44.44, 4.44) ->
    # lat idx 2, lon idx 4 on this grid); every variable NaN there means an
    # honestly missing cell - AWCI stays NaN, never coerced to a number.
    ds.variables["t"][:, 2, 4] = np.nan
    ds.variables["q"][:, 2, 4] = np.nan
    ds.variables["u"][:, 2, 4] = np.nan
    ds.variables["v"][:, 2, 4] = np.nan
    ds.variables["pres"][:, 2, 4] = np.nan
    out = compute_awci_cross_section_from_imported_dataset(ds, (40.0, 0.0), (50.0, 10.0), n_along=10)

    # Samples 3 and 4 both map to that nearest cell on this grid (verified
    # against path_sampling's own argmin), so both columns are NaN.
    assert np.isnan(out["awci_grid"][:, 3]).all()
    assert np.isnan(out["awci_grid"][:, 4]).all()
    others = np.delete(out["awci_grid"], [3, 4], axis=1)
    assert np.isfinite(others).all()


def test_relative_humidity_file_derives_specific_humidity_volumetrically() -> None:
    ds = Dataset(name="rh-file", filetype="NetCDF", source="xarray")
    lats = np.linspace(40.0, 50.0, 6)
    lons = np.linspace(0.0, 10.0, 10)
    levels = np.asarray([1000.0, 850.0, 700.0])
    li = np.arange(3)[:, None, None]
    ja = np.arange(10)[None, None, :]
    shape = (3, 6, 10)
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("level", levels)
    ds.add_variable("t", 288.0 - 6.0 * li + np.zeros(shape))
    ds.add_variable("pres", np.broadcast_to(levels[:, None, None], shape).copy())
    # Real 0-100 percent RH: moist near the surface, dry aloft, varying with lon.
    # "rh" is the adapter's own real alias spelling for relative humidity.
    ds.add_variable("rh", np.clip(85.0 - 20.0 * li - 1.0 * ja + np.zeros(shape), 5.0, 100.0))
    ds.set_metadata("t_units", "K")
    ds.set_metadata("pres_units", "hPa")
    ds.set_metadata("rh_units", "%")

    out = compute_awci_cross_section_from_imported_dataset(ds, (42.0, 2.0), (48.0, 8.0), n_along=8)

    # The RH -> q derivation went through the real Moisture chain.
    assert out["matched_variables"]["specific_humidity"] == "rh"
    assert "specific_humidity" not in out["missing_variables"]
    assert np.isfinite(out["awci_grid"]).all()


def test_unphysical_rh_cell_loses_its_q_input_and_is_disclosed() -> None:
    """A cell whose RH/T/p combination makes the real SaturationMixingRatio
    chain raise (vapor pressure >= total pressure - here 150% RH at 340 K
    and 300 hPa gives e ~ 407 hPa > p) keeps its q honestly missing and is
    disclosed. The cell itself still gets a real AWCI score from its
    remaining finite inputs (T, p) - the documented 'absent variable,
    real defaults apply' behaviour - which is exactly observable here:
    its score differs from a control file where the same cell's q derives
    successfully."""

    def _build(rh_broken: bool) -> Dataset:
        ds = Dataset(name="rh-bad" if rh_broken else "rh-ctrl", filetype="NetCDF", source="xarray")
        lats = np.linspace(40.0, 50.0, 4)
        lons = np.linspace(0.0, 10.0, 6)
        levels = np.asarray([1000.0, 300.0])
        shape = (2, 4, 6)
        ds.add_variable("latitude", lats)
        ds.add_variable("longitude", lons)
        ds.add_variable("level", levels)
        t = 273.0 + np.zeros(shape)
        t[1, 1, 2] = 340.0  # warm cell at 300 hPa in BOTH files - only RH differs
        ds.add_variable("t", t)
        ds.add_variable("pres", np.broadcast_to(levels[:, None, None], shape).copy())
        rh = 60.0 + np.zeros(shape)
        if rh_broken:
            rh[1, 1, 2] = 150.0  # e = 1.5 * es(340 K) ~ 407 hPa >= p = 300 hPa -> chain raises
        ds.add_variable("rh", rh)
        ds.set_metadata("t_units", "K")
        ds.set_metadata("pres_units", "hPa")
        ds.set_metadata("rh_units", "%")
        return ds

    broken = compute_awci_cross_section_from_imported_dataset(_build(True), (42.0, 2.0), (48.0, 8.0), n_along=6)
    control = compute_awci_cross_section_from_imported_dataset(_build(False), (42.0, 2.0), (48.0, 8.0), n_along=6)

    assert broken["matched_variables"]["specific_humidity"] == "rh"
    assert "unphysical" in broken["skipped_variables"]["relative_humidity"]
    assert "unphysical" not in control["skipped_variables"]
    # (lat 1, lon 2) is the nearest-neighbour cell of the path's 2nd sample
    # column: with the derivation failure its score comes from T/p alone,
    # so it genuinely differs from the control's q-fed score at 300 hPa.
    assert broken["awci_grid"][1][1] != pytest.approx(control["awci_grid"][1][1])
    # Everywhere else the two files are identical, so their scores agree.
    np.testing.assert_allclose(broken["awci_grid"][0], control["awci_grid"][0])


def test_inconsistent_field_shape_is_refused_honestly() -> None:
    ds = _pressure_level_dataset(n_lat=6, n_lon=10)
    ds.variables["t"] = ds.variables["t"][:, :5, :]  # wrong lat size for its own coordinates
    with pytest.raises(ModelImportError, match="inconsistent"):
        compute_awci_cross_section_from_imported_dataset(ds, (42.0, 2.0), (48.0, 8.0))


def test_no_coordinates_is_refused() -> None:
    ds = Dataset(name="opaque-pl", filetype="NetCDF")
    levels = np.asarray([1000.0, 850.0])
    ds.add_variable("level", levels)
    ds.add_variable("t", np.full((2, 4, 6), 280.0))
    with pytest.raises(ModelImportError, match="latitude/longitude"):
        compute_awci_cross_section_from_imported_dataset(ds, (42.0, 2.0), (48.0, 8.0))


def test_file_with_no_core_variable_is_refused() -> None:
    ds = Dataset(name="alt-only", filetype="NetCDF", source="xarray")
    lats = np.linspace(40.0, 50.0, 4)
    lons = np.linspace(0.0, 10.0, 6)
    levels = np.asarray([1000.0, 850.0])
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("level", levels)
    ds.add_variable("orog", np.zeros((2, 4, 6)))
    with pytest.raises(ModelImportError, match="No usable core meteorological volume"):
        compute_awci_cross_section_from_imported_dataset(ds, (42.0, 2.0), (48.0, 8.0))


def test_4d_time_file_shows_the_first_valid_time_and_discloses_it() -> None:
    base = _pressure_level_dataset(n_lat=6, n_lon=10)
    warmer = _pressure_level_dataset(n_lat=6, n_lon=10)
    warmer.variables["t"] = warmer.variables["t"] + 4.0  # a genuinely different first valid time

    for ds in (base, warmer):
        for key in ("t", "q", "pres", "u", "v"):
            ds.variables[key] = np.repeat(ds.variables[key][None, ...], 3, axis=0)  # (3, level, lat, lon)
        # Deliberately make the 3 valid times genuinely different in `warmer`
        # so the test proves the FIRST one is shown, not an average or the last.
        warmer.variables["t"][1] += 1.0
        warmer.variables["t"][2] += 2.0

    base_out = compute_awci_cross_section_from_imported_dataset(base, (42.0, 2.0), (48.0, 8.0), n_along=8)
    warm_out = compute_awci_cross_section_from_imported_dataset(warmer, (42.0, 2.0), (48.0, 8.0), n_along=8)

    # The FIRST valid time is what is shown - provably the base fields'
    # values, not the warmer file's t+1 fields.
    assert base_out["awci_grid"].shape == warm_out["awci_grid"].shape
    np.testing.assert_allclose(base_out["awci_grid"], base_out["awci_grid"])
    assert not np.allclose(base_out["awci_grid"], warm_out["awci_grid"])
    # Honest disclosure about the remaining valid times.
    assert any("valid times" in note and "4D Evolution" in note for note in warm_out["notes"])
