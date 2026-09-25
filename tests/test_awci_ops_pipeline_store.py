import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.pipeline import LEVEL_LAYERS, SURFACE_LAYERS, compute_step
from acf.awci.ops.source_ecmwf import parse_index
from acf.awci.ops.store import CubeStore, CubeWriter, apply_retention, run_id
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
DOMAIN = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)
PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


def _fields(step: int):
    stem = f"20260925000000-{step}h-oper-fc"
    data = (FIXTURE / f"{stem}.grib2").read_bytes()
    msgs = [data[e.offset : e.offset + e.length] for e in parse_index((FIXTURE / f"{stem}.index").read_text())]
    return decode_messages(msgs, [DOMAIN])["fixture"]


def _write_cube(root: Path, steps=(0, 3), fail_step: int | None = None) -> dict:
    f0 = _fields(0)
    elevation = interpolate_real_terrain_elevation(f0.lats, f0.lons)
    writer = CubeWriter(root, DOMAIN, RUN, f0.lats, f0.lons, f0.levels_hpa, list(steps), PROFILE)
    missing = []
    for i, step in enumerate(steps):
        if step == fail_step:
            missing.append(step)
            continue
        writer.write_step(i, compute_step(_fields(step), elevation, PROFILE), elevation)
    return writer.finalize("partial" if missing else "complete", missing, {})


def test_compute_step_shapes_and_ranges() -> None:
    f = _fields(3)
    layers = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
    for name in LEVEL_LAYERS:
        assert layers[name].shape == (12, 9, 9), name
    for name in SURFACE_LAYERS:
        assert layers[name].shape == (9, 9), name
    awci = layers["awci"]
    assert np.all((awci[np.isfinite(awci)] >= 0) & (awci[np.isfinite(awci)] <= 100))
    assert np.isfinite(awci).mean() > 0.9


def test_cube_roundtrip_manifest_and_nan_not_zero(tmp_path: Path) -> None:
    manifest = _write_cube(tmp_path)
    assert manifest["status"] == "complete" and manifest["steps"] == [0, 3]
    assert manifest["license"] == "CC-BY-4.0" and manifest["profile"] == "operational-v1"
    store = CubeStore(tmp_path)
    assert [r["run"] for r in store.runs("fixture")] == ["2026092500"]
    ds = store.dataset("fixture", "2026092500")
    assert ds["awci"].shape == (2, 12, 9, 9)
    assert ds["elevation"].shape == (9, 9)
    assert not (tmp_path / "fixture" / "2026092500.tmp").exists()


def test_partial_run_is_marked(tmp_path: Path) -> None:
    manifest = _write_cube(tmp_path, fail_step=3)
    assert manifest["status"] == "partial" and manifest["missing_steps"] == [3]
    ds = CubeStore(tmp_path).dataset("fixture", "2026092500")
    assert np.isnan(ds["awci"].isel(step=1)).all()


def test_two_ingestions_are_identical(tmp_path: Path) -> None:
    _write_cube(tmp_path / "a")
    _write_cube(tmp_path / "b")
    a = CubeStore(tmp_path / "a").dataset("fixture", "2026092500")
    b = CubeStore(tmp_path / "b").dataset("fixture", "2026092500")
    for name in a.data_vars:
        np.testing.assert_array_equal(a[name].values, b[name].values)


def test_retention_keeps_newest(tmp_path: Path) -> None:
    for rid in ("2026092400", "2026092406", "2026092412"):
        d = tmp_path / "fixture" / rid
        d.mkdir(parents=True)
        (d / "manifest.json").write_text(json.dumps({"run": rid}))
    assert apply_retention(tmp_path, "fixture", keep=2) == ["2026092400"]
    assert sorted(p.name for p in (tmp_path / "fixture").iterdir()) == ["2026092406", "2026092412"]


def test_run_id() -> None:
    assert run_id(RUN) == "2026092500"


def test_unknown_run_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        CubeStore(tmp_path).manifest("fixture", "2026010100")
