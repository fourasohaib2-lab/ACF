from datetime import UTC, datetime
from pathlib import Path

import pytest

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run, main, parse_steps
from acf.awci.ops.store import CubeStore
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)


def test_parse_steps() -> None:
    assert parse_steps("0-72/3")[:3] == [0, 3, 6] and parse_steps("0-72/3")[-1] == 72
    assert parse_steps("0,3") == [0, 3]
    with pytest.raises(ValueError):
        parse_steps("0-10/0")


def test_ingest_complete(tmp_path: Path) -> None:
    manifests = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(), tmp_path, [0, 3])
    assert manifests["fixture"]["status"] == "complete"
    assert CubeStore(tmp_path).dataset("fixture", "2026092500")["awci"].shape == (2, 12, 9, 9)


def test_ingest_partial_when_a_step_fails(tmp_path: Path) -> None:
    manifests = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(3,)), tmp_path, [0, 3])
    assert manifests["fixture"]["status"] == "partial" and manifests["fixture"]["missing_steps"] == [3]


def test_ingest_failed_when_every_step_fails(tmp_path: Path) -> None:
    manifests = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(0, 3)), tmp_path, [0, 3])
    assert manifests["fixture"]["status"] == "failed"
    assert CubeStore(tmp_path).runs("fixture") == []


def test_cli_exit_codes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("acf.awci.ops.ingest.UrllibFetcher", lambda: FixtureFetcher())
    domains = tmp_path / "domains.json"
    domains.write_text('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
                       '"west": 2, "east": 4, "default": true}]}')
    code = main(["--run", "2026092500", "--steps", "0,3", "--domains-file", str(domains),
                 "--data-dir", str(tmp_path / "data")])
    assert code == 0
    assert (tmp_path / "data" / "fixture" / "2026092500" / "manifest.json").exists()
