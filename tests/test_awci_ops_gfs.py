"""GFS adapter (SP6): real index, message choice per step, derived fields, ttr rebuild, real fixture ingestion."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from acf.awci.ops.accum import olr_w_m2
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.kinematics import EARTH_RADIUS_M, horizontal_divergence
from acf.awci.ops.source_ecmwf import MissingFieldsError
from acf.awci.ops.source_gfs import (
    GfsRunState,
    bucket_start,
    gfs_step_urls,
    parse_gfs_index,
    ptype_codes,
    select_gfs_entries,
    wanted_keys,
)
from acf.awci.ops.thermo import ifs_relative_humidity_pct, ifs_saturation_vapor_pressure_hpa, vapor_pressure_hpa
from tests.awci_ops_support import DOMAIN, GFS_FIXTURE, FixtureFetcher, GfsFixtureFetcher

RUN = datetime(2026, 9, 25, tzinfo=UTC)


def test_urls_and_real_index() -> None:
    grib, idx = gfs_step_urls(RUN, 3)
    assert grib.endswith("/gfs.20260925/00/atmos/gfs.t00z.pgrb2.0p25.f003") and idx == grib + ".idx"
    entries = parse_gfs_index((GFS_FIXTURE / "gfs.t00z.pgrb2.0p25.f003.idx").read_text())
    assert entries[0].var == "TMP" and entries[0].level == "1000 mb" and entries[0].offset == 0
    assert all(e.length == n.offset - e.offset for e, n in zip(entries, entries[1:])) and entries[-1].length is None


def test_messages_per_step_follow_the_gfs_buckets() -> None:
    assert "apcp" not in wanted_keys(0) and wanted_keys(0)["2t"] == ("TMP", "2 m above ground", "anl")
    assert wanted_keys(9)["ulwrf_toa"] == ("ULWRF", "top of atmosphere", "6-9 hour ave fcst")
    assert wanted_keys(12)["ulwrf_toa"][2] == "6-12 hour ave fcst" and wanted_keys(12)["apcp"][2] == "0-12 hour acc fcst"
    assert [bucket_start(s) for s in (3, 6, 9, 12, 13)] == [0, 0, 6, 6, 12]
    entries = parse_gfs_index((GFS_FIXTURE / "gfs.t00z.pgrb2.0p25.f003.idx").read_text())
    assert len(select_gfs_entries(entries, 3)) == 93
    with pytest.raises(MissingFieldsError, match="apcp"):
        select_gfs_entries([e for e in entries if e.var != "APCP"], 3)


def test_ifs_mixed_phase_humidity() -> None:
    assert ifs_saturation_vapor_pressure_hpa(np.array(273.16)) == pytest.approx(6.1121)  # a1 at T0
    t = 261.66  # alpha = ((261.66 - 250.16) / 23)^2 = 0.25
    ew = 611.21 * np.exp(17.502 * (t - 273.16) / (t - 32.19)) / 100
    ei = 611.21 * np.exp(22.587 * (t - 273.16) / (t + 0.7)) / 100
    assert ifs_saturation_vapor_pressure_hpa(np.array(t)) == pytest.approx(0.25 * ew + 0.75 * ei)
    q = 0.003
    rh = ifs_relative_humidity_pct(np.array(t), np.array(q), np.array(600.0))
    assert rh == pytest.approx(vapor_pressure_hpa(q, 600.0) / (0.25 * ew + 0.75 * ei) * 100)
    assert ifs_relative_humidity_pct(np.array(240.0), np.array(0.0006), np.array(500.0)) > 100  # not capped (ice)


def test_divergence_of_analytic_winds() -> None:
    lats, lons = np.arange(30, 40.01, 0.25), np.arange(0, 10.01, 0.25)
    ones = np.ones((lats.size, lons.size))
    solid = 10 * np.cos(np.radians(lats))[:, None] * ones  # solid-body rotation: non-divergent
    assert np.abs(horizontal_divergence(solid, 0 * ones, lats, lons)).max() == pytest.approx(0, abs=1e-15)
    v = 5 * np.cos(np.radians(lats))[:, None] * ones  # div = -2 V sin(phi) / R
    exact = -2 * 5 * np.sin(np.radians(lats))[:, None] / EARTH_RADIUS_M
    np.testing.assert_allclose(horizontal_divergence(0 * ones, v, lats, lons)[2:-2], (exact * ones)[2:-2], rtol=1e-4)


def test_precipitation_type_codes() -> None:
    crain, csnow, cfrzr, cicep = (np.array(x, dtype=float) for x in (
        [0, 1, 0, 1, 1, 0, 1], [0, 0, 1, 1, 0, 0, np.nan], [0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 1, 0]))
    np.testing.assert_array_equal(ptype_codes(crain, csnow, cfrzr, cicep), [0, 1, 5, 7, 3, 8, np.nan])


def test_top_of_atmosphere_accumulation_is_rebuilt_from_the_buckets() -> None:
    state, one = GfsRunState(), np.ones((2, 2))
    ttr = {s: state.ttr("d", s, m * one) for s, m in ((3, 250), (6, 240), (9, 230), (12, 220))}
    assert ttr[3] == pytest.approx(-250 * 3 * 3600 * one) and ttr[6] == pytest.approx(-240 * 6 * 3600 * one)
    np.testing.assert_allclose(olr_w_m2(ttr[6], ttr[3], 3), 230)  # (240 x 6 - 250 x 3) / 3
    np.testing.assert_allclose(olr_w_m2(ttr[9], ttr[6], 3), 230)
    np.testing.assert_allclose(olr_w_m2(ttr[12], ttr[9], 3), 210)  # (220 x 6 - 230 x 3) / 3
    assert GfsRunState().ttr("d", 9, 230 * one) is None  # bucket start (6 h) never seen: no invented value


@pytest.fixture(scope="module")
def gfs_cube(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    root = tmp_path_factory.mktemp("gfs")
    manifests = ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), GfsFixtureFetcher(),
                           root / "gfs", [0, 3, 6], model="gfs")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    return root, manifests["fixture"]


def test_real_gfs_run_through_the_unchanged_pipeline(gfs_cube: tuple[Path, dict]) -> None:
    root, manifest = gfs_cube
    assert manifest["status"] == "complete" and manifest["model_id"] == "gfs"
    assert "NOAA" in manifest["attribution"] and "sf" in manifest["definition_differences"]
    saved = json.loads((root / "gfs" / "fixture" / "2026092500" / "manifest.json").read_text())
    assert saved["license"] == "public domain (NOAA)"
    gfs = xr.open_dataset(root / "gfs" / "fixture" / "2026092500" / "cube.nc")
    ifs = xr.open_dataset(root / "fixture" / "2026092500" / "cube.nc")
    np.testing.assert_array_equal(gfs["lat"].values, ifs["lat"].values)  # same 0.25° grid after cropping
    np.testing.assert_array_equal(gfs["lon"].values, ifs["lon"].values)
    assert np.isnan(gfs["snowfall_mm"].values).all()  # no GFS snowfall: said, never zero
    teff = gfs["cloud_top_teff_k"].values
    assert np.isnan(teff[0]).all() and np.isfinite(teff[1:]).all() and (teff[1:] > 180).all() and (teff[1:] < 320).all()
    awci = gfs["awci"].values
    assert np.nanmin(awci) >= 0 and np.nanmax(awci) <= 100 and np.isfinite(awci).any()
    r = gfs["r"].values
    assert np.nanmin(r) >= 0 and np.isfinite(r).any()


def test_a_missing_gfs_step_breaks_the_accumulations_honestly(tmp_path: Path) -> None:
    m = ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), GfsFixtureFetcher(fail_steps=(3,)),
                   tmp_path, [0, 3, 6], model="gfs")["fixture"]
    assert m["status"] == "partial" and m["missing_steps"] == [3]
    ds = xr.open_dataset(tmp_path / "fixture" / "2026092500" / "cube.nc")
    assert np.isnan(ds["cloud_top_teff_k"].values[2]).all()  # 6 h without 3 h: no interval, NaN
