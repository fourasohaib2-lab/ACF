"""tools/awci/verify_soundings.py on the real IFS and GFS fixtures of the same run and the real Algiers sounding."""

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from acf.awci.obs.sounding import parse_uwyo_csv
from acf.awci.obs.store import ObsStore
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from tests.awci_ops_support import DOMAIN, FixtureFetcher, GfsFixtureFetcher

spec = importlib.util.spec_from_file_location("verify_soundings",
                                              Path(__file__).parents[1] / "tools" / "awci" / "verify_soundings.py")
vs = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(vs)  # type: ignore[union-attr]

RUN = datetime(2026, 9, 25, tzinfo=UTC)
CSV = (Path(__file__).parent / "data" / "awci_soundings" / "uwyo_60390_2026092500.csv").read_text()


def test_both_models_pooled_and_per_lead_time(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    ingest_run(RUN, [DOMAIN], profile, FixtureFetcher(), tmp_path, [0, 3])
    ingest_run(RUN, [DOMAIN], profile, GfsFixtureFetcher(), tmp_path / "gfs", [0, 3], model="gfs")
    ObsStore(tmp_path, DOMAIN.name).add_soundings([parse_uwyo_csv(CSV, "60390", RUN)])  # type: ignore[list-item]
    domains = tmp_path / "domains.json"
    domains.write_text(json.dumps({"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37,
                                                "west": 2, "east": 4, "default": True}]}))
    out = tmp_path / "report.json"
    assert vs.main(["--data-dir", str(tmp_path), "--domain", "fixture", "--runs", "2026092500",
                    "--domains-file", str(domains), "--out", str(out)]) == 0
    report = json.loads(out.read_text())
    for model in ("ifs", "gfs"):
        r = report["models"][model]
        assert r["soundings"] == 1 and r["by_step"]["0"]["soundings"] == 1 and r["total"]["t"]["n"] >= 10
        assert abs(r["total"]["t"]["bias"]) < 3.0  # analysis step (+0 h): mean column error of a few kelvin at most
    assert "| IFS | 1 (" in capsys.readouterr().out
