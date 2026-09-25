"""SP1C pipeline integration on the real cropped IFS fixtures (dry and wet)."""

from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from acf.awci.ops.clouds import CLOUD_LEVEL_LAYERS, CLOUD_SURFACE_LAYERS
from acf.awci.ops.decode import decode_messages
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.pipeline import compute_step
from acf.awci.ops.registry import LAYERS, LEVEL_LAYERS, SURFACE_LAYERS
from acf.awci.ops.source_ecmwf import parse_index
from acf.awci.ops.store import CubeStore
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation
from tests.awci_ops_support import DOMAIN, FIXTURE, WET_DOMAIN, WET_FIXTURE, FixtureFetcher

PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


def _fields(root: Path, domain, step: int):
    stem = f"20260925000000-{step}h-oper-fc"
    data = (root / f"{stem}.grib2").read_bytes()
    msgs = [data[e.offset:e.offset + e.length] for e in parse_index((root / f"{stem}.index").read_text())]
    return decode_messages(msgs, [domain])[domain.name]


def test_registry_lists_every_cloud_layer() -> None:
    assert set(CLOUD_LEVEL_LAYERS) <= set(LEVEL_LAYERS) and set(CLOUD_SURFACE_LAYERS) <= set(SURFACE_LAYERS)
    for name in (*CLOUD_LEVEL_LAYERS, *CLOUD_SURFACE_LAYERS, "cloud_cover_bias", "cloud_top_teff_k",
                 "column_condensate", "snowfall_mm", "snow_depth_cm", "freezing_precip_mm"):
        assert name in LAYERS, name


def test_accumulations_need_the_previous_step() -> None:
    f0, f3 = _fields(FIXTURE, DOMAIN, 0), _fields(FIXTURE, DOMAIN, 3)
    elev = interpolate_real_terrain_elevation(f3.lats, f3.lons)
    alone = compute_step(f3, elev, PROFILE)
    assert np.isnan(alone["cloud_top_teff_k"]).all() and np.isnan(alone["snowfall_mm"]).all()
    chained = compute_step(f3, elev, PROFILE, previous=f0, interval_h=3.0)
    assert np.isfinite(chained["cloud_top_teff_k"]).all()
    assert (180.0 < chained["cloud_top_teff_k"]).all() and (chained["cloud_top_teff_k"] < 320.0).all()


def test_real_fields_give_consistent_cloud_diagnostics() -> None:
    for root, domain in ((FIXTURE, DOMAIN), (WET_FIXTURE, WET_DOMAIN)):
        f = _fields(root, domain, 3)
        out = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
        tot = out["cloud_cover_total_diag"]
        assert ((0.0 <= tot) & (tot <= 1.0)).all()
        for e in ("low", "mid", "high"):
            assert (out[f"cloud_cover_{e}"] <= tot + 1e-12).all()
        np.testing.assert_allclose(out["cloud_cover_bias"], tot - f.sfc["tcc"])
        assert (out["column_condensate"] >= 0.0).all()


def test_wet_fixture_exercises_precipitating_genera() -> None:
    f = _fields(WET_FIXTURE, WET_DOMAIN, 3)
    out = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
    assert (out["precip_rate"] > 0.1).any()
    assert (np.isin(out["genus_low"], (5, 8, 9)) | np.isin(out["genus_mid"], (5, 8, 9))).any()  # Ns, Cu or Cb


def test_manifest_records_cloud_consistency_and_intervals(tmp_path: Path) -> None:
    manifest = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(), tmp_path, [0, 3])["fixture"]
    assert manifest["accumulation_interval_h"] == [None, 3]
    assert [c["step"] for c in manifest["cloud_consistency"]] == [0, 3]
    assert manifest["cloud_profile"] == "cloud-v1" and manifest["cloud_status"] in ("ok", "degraded")
    ds = CubeStore(tmp_path).dataset("fixture", "2026092500")
    assert np.isnan(ds["snowfall_mm"].isel(step=0)).all() and np.isfinite(ds["snowfall_mm"].isel(step=1)).all()


def test_failed_previous_step_nulls_next_accumulations(tmp_path: Path) -> None:
    manifest = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(0,)), tmp_path, [0, 3])["fixture"]
    assert manifest["accumulation_interval_h"] == [None, None]
    assert np.isnan(CubeStore(tmp_path).dataset("fixture", "2026092500")["cloud_top_teff_k"].isel(step=1)).all()


def test_heights_above_sea_are_counted_from_sea_level_not_bathymetry() -> None:
    f = _fields(WET_FIXTURE, WET_DOMAIN, 3)  # open ocean: SRTM15+ gives -2000 to -3800 m (bathymetry)
    elevation = interpolate_real_terrain_elevation(f.lats, f.lons)
    assert (elevation < -1000).all() and (f.sfc["lsm"] < 0.5).all()
    out = compute_step(f, elevation, PROFILE)
    assert (out["surface_height_m"] == 0.0).all()
    ceiling = out["ceiling_m"][np.isfinite(out["ceiling_m"])]
    assert ceiling.size and (ceiling <= 6000.0).all()
    gh = f.pl["gh"]
    for iy, ix in zip(*np.nonzero(np.isfinite(out["ceiling_m"]))):
        assert np.isclose(gh[:, iy, ix], out["ceiling_m"][iy, ix]).any()  # base = gh of a level above 0 m
