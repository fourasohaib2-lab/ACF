"""RHc calibration recovers known critical humidities from a field built with them."""

from dataclasses import replace

import numpy as np

from acf.awci.ops.calibration import _cover, calibrate_rhc
from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import etage_codes

LEVELS = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100], dtype=float)


def test_recovers_known_rhc() -> None:
    rng = np.random.default_rng(20260925)
    base = replace(load_cloud_profile(), rh_critical={"low": 0.80, "mid": 0.70, "high": 0.70})
    truth = replace(base, rh_critical={"low": 0.775, "mid": 0.65, "high": 0.725})
    n, ny, nx = 4, 20, 20
    r = rng.uniform(40.0, 100.0, size=(n, len(LEVELS), ny, nx))
    sp = rng.uniform(900.0, 1020.0, size=(n, ny, nx))
    tcc = np.stack([_cover(r[k], etage_codes(LEVELS, sp[k], truth), LEVELS[:, None, None] > sp[k][None], truth)
                    for k in range(n)])
    result = calibrate_rhc(r, sp, LEVELS, tcc, base)
    for name, value in truth.rh_critical.items():
        assert abs(result["rh_critical"][name] - value) <= 0.025 + 1e-9, (name, result)
    assert result["rmse_after"] < result["rmse_before"] and result["n_cells"] == n * ny * nx


def test_tool_runs_on_a_real_cube_and_writes_a_calibration_record(tmp_path, capsys) -> None:
    import json
    import shutil
    import sys
    from datetime import UTC, datetime
    from pathlib import Path

    from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH
    from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
    from acf.awci.ops.ingest import ingest_run
    from tests.awci_ops_support import DOMAIN, FixtureFetcher

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "awci"))
    import calibrate_cloud_rhc

    ingest_run(datetime(2026, 9, 25, 0, tzinfo=UTC), [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH),
               FixtureFetcher(), tmp_path, [0, 3])
    profile = tmp_path / "cloud.json"
    shutil.copy(DEFAULT_CLOUD_PROFILE_PATH, profile)
    major, minor, _ = (int(x) for x in json.loads(profile.read_text())["version"].split("."))
    calibrate_cloud_rhc.main(["--domain", "fixture", "--runs", "2026092500", "--steps", "0,3",
                              "--data-dir", str(tmp_path), "--profile", str(profile), "--write"])
    printed = json.loads(capsys.readouterr().out)
    written = json.loads(profile.read_text())
    assert printed["steps"] == [0, 3] and printed["n_cells"] > 0
    assert written["version"] == f"{major}.{minor + 1}.0" and written["calibration"]["rmse_after"] <= printed["rmse_before"]
    assert written["rh_critical"] == printed["rh_critical"]
    assert load_cloud_profile(profile).calibration is not None
