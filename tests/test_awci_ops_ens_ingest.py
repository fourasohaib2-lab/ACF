"""acf-awci-ens: stream IFS ENS members through the pipeline, store exact counts atomically."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import xarray as xr

from acf.awci.ops.ens_ingest import ingest_ens_run, main
from acf.awci.ops.ens_store import EnsStore
from acf.awci.ops.source_ecmwf import FetchError
from tests.awci_ops_support import DOMAIN, ENS_FIXTURE, FixtureFetcher, ens_member_layers

RUN = datetime(2026, 9, 26, 0, tzinfo=UTC)


class DropMember(FixtureFetcher):
    """Serves the real fixture but fails every download of one member's messages."""

    def __init__(self, member: int) -> None:
        super().__init__(root=ENS_FIXTURE)
        self.member = member
        self.bad: set[tuple[str, int]] = set()
        for step in (0, 6):
            index = (ENS_FIXTURE / f"20260926000000-{step}h-enfo-ef.index").read_text().splitlines()
            self.bad |= {(f"{step}h", json.loads(line)["_offset"]) for line in index if json.loads(line)["number"] == str(member)}

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        if (url.rsplit("/", 1)[1].split("-")[1], offset) in self.bad:
            raise FetchError(url)
        return super().get_range(url, offset, length)


def test_members_are_streamed_and_counted_exactly(tmp_path: Path) -> None:
    manifest = ingest_ens_run(RUN, DOMAIN, FixtureFetcher(root=ENS_FIXTURE), tmp_path, steps=[0, 6], members=[1, 2, 3, 4])
    assert manifest["status"] == "complete" and manifest["members_used"] == {"0": 4, "6": 4}
    assert manifest["products"]["p_cloud_bkn"]["dims"] == "level"
    store = EnsStore(tmp_path)
    assert [r["run"] for r in store.runs("fixture")] == ["2026092600"]
    ds = store.dataset("fixture", "2026092600")
    expected = sum((m["cloud_fraction"] >= 0.625).astype(int) for m in ens_member_layers(ENS_FIXTURE, 6, (1, 2, 3, 4)))
    np.testing.assert_array_equal(ds["p_cloud_bkn_count"].isel(step=1).values, expected)
    assert int(ds["p_convection_n"].isel(step=0).max()) == 4
    assert not list(tmp_path.rglob("*.tmp"))  # atomic publication


def test_a_failing_member_is_excluded_and_recorded(tmp_path: Path) -> None:
    manifest = ingest_ens_run(RUN, DOMAIN, DropMember(3), tmp_path, steps=[0, 6], members=[1, 2, 3, 4])
    assert manifest["members_used"] == {"0": 3, "6": 3}
    assert manifest["failed_members"] == {"0": [3], "6": [3]}
    assert manifest["status"] == "complete"
    ds = EnsStore(tmp_path).dataset("fixture", "2026092600")
    assert int(ds["p_awci_high_n"].max()) <= 3


def test_a_missing_step_is_reported_and_never_filled(tmp_path: Path) -> None:
    manifest = ingest_ens_run(RUN, DOMAIN, FixtureFetcher(root=ENS_FIXTURE), tmp_path, steps=[0, 6, 12], members=[1, 2])
    assert manifest["missing_steps"] == [12] and manifest["status"] == "partial"
    ds: xr.Dataset = EnsStore(tmp_path).dataset("fixture", "2026092600")
    assert int(ds["p_cloud_bkn_n"].isel(step=2).max()) == 0  # nothing written for +12 h


def test_command_line(tmp_path: Path, monkeypatch) -> None:
    domains = tmp_path / "domains.json"
    domains.write_text(json.dumps({"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, "west": 2,
                                                "east": 4, "default": True}]}))
    monkeypatch.setattr("acf.awci.ops.ens_ingest.UrllibFetcher", lambda: FixtureFetcher(root=ENS_FIXTURE))
    assert main(["--run", "2026092600", "--domain", "fixture", "--steps", "0,6", "--members", "1-2",
                 "--domains-file", str(domains), "--data-dir", str(tmp_path)]) == 0
    assert EnsStore(tmp_path).manifest("fixture", "2026092600")["members_requested"] == [1, 2]
