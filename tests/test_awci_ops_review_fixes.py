"""Regression tests for the SP1 final-review findings (below-ground levels, icing RH, import hygiene, atomic rerun)."""

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.hazards import icing_potential
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.pipeline import LEVEL_LAYERS, compute_step
from acf.awci.ops.source_ecmwf import parse_index
from acf.awci.ops.store import CubeStore
from acf.awci.ops.thermo import relative_humidity_pct
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation
from tests.awci_ops_support import DOMAIN, FIXTURE, FixtureFetcher

PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


def _fields():
    stem = "20260925000000-3h-oper-fc"
    data = (FIXTURE / f"{stem}.grib2").read_bytes()
    msgs = [data[e.offset : e.offset + e.length] for e in parse_index((FIXTURE / f"{stem}.index").read_text())]
    return decode_messages(msgs, [DOMAIN])["fixture"]


def test_levels_below_surface_pressure_are_nan_in_every_level_layer() -> None:
    f = _fields()
    layers = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
    sp_hpa = f.sfc["sp"] / 100.0
    underground = f.levels_hpa[:, None, None] > sp_hpa[None]
    assert underground.any() and (~underground).any()  # the real fixture has both cases
    for name in LEVEL_LAYERS:
        assert np.isnan(layers[name][underground]).all(), name
    assert np.isfinite(layers["awci"][~underground]).all()


def test_icing_uses_rh_over_water_not_ifs_r() -> None:
    f = _fields()
    f.pl["r"] = np.full_like(f.pl["r"], 100.0)  # IFS r is w.r.t. ice below -23 degC: must not drive the flag
    layers = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
    p3d = f.levels_hpa[:, None, None] * np.ones_like(f.pl["t"])
    expected = icing_potential(f.pl["t"], relative_humidity_pct(f.pl["t"], f.pl["q"], p3d))
    above = f.levels_hpa[:, None, None] <= (f.sfc["sp"] / 100.0)[None]
    assert (expected[above] == 0).any()  # the real q gives dry cold cells where r=100 would wrongly flag icing
    np.testing.assert_array_equal(layers["icing_potential"][above], expected[above])


def test_router_imports_without_eccodes() -> None:
    code = "import sys; sys.modules['eccodes'] = None; import acf.web.awci_router, acf.web.awci_app"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parents[1], env={"PYTHONPATH": "src", "PATH": ""})
    assert result.returncode == 0, result.stderr[-2000:]


def test_rerun_never_downgrades_a_complete_run(tmp_path: Path) -> None:
    assert ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(), tmp_path, [0, 3])["fixture"]["status"] == "complete"
    rerun = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(3,)), tmp_path, [0, 3])["fixture"]
    assert rerun["status"] == "complete" and rerun["rejected_rerun_status"] == "partial"
    assert CubeStore(tmp_path).manifest("fixture", "2026092500")["status"] == "complete"
    assert np.isfinite(CubeStore(tmp_path).dataset("fixture", "2026092500")["awci"].isel(step=1)).any()
    assert sorted(p.name for p in (tmp_path / "fixture").iterdir()) == ["2026092500"]


def test_forced_rerun_replaces_and_leaves_no_old_dir(tmp_path: Path) -> None:
    ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(), tmp_path, [0, 3])
    rerun = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(3,)), tmp_path, [0, 3], force=True)
    assert rerun["fixture"]["status"] == "partial"
    assert sorted(p.name for p in (tmp_path / "fixture").iterdir()) == ["2026092500"]
