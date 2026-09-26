"""acf-awci-auto: run detection by probing, no re-download of a complete run, retries, observation cadence,
deletion after a week (the newest run always kept), single instance, and the acf-awci-web --auto wiring."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from acf.awci.obs.store import ObsStore
from acf.awci.ops.auto import (
    AutoConfig,
    AutoIngest,
    InstanceLock,
    wait,
    apply_age_retention,
    build_parser,
    candidate_runs,
    config_from_args,
    latest_published,
)
from acf.awci.ops.source_ecmwf import FetchError, ens_step_urls, step_urls
from acf.awci.ops.source_gfs import gfs_step_urls
from tests.awci_ops_support import DOMAIN

NOW = datetime(2026, 9, 26, 15, 7, tzinfo=UTC)


class ProbeFetcher:
    """Answers the index URLs of the published runs only; records every probe."""

    def __init__(self, published: set[str]) -> None:
        self.published, self.probes = published, []

    def get_text(self, url: str) -> str:
        self.probes.append(url)
        if url not in self.published:
            raise FetchError(f"404 {url}")
        return ""

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        raise AssertionError("the scheduler never downloads data itself")


def _manifest(folder: Path, status: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(json.dumps({"status": status}))


class Recorder:
    def __init__(self, root: Path, status: str = "complete", fail: bool = False) -> None:
        self.root, self.status, self.fail = root, status, fail
        self.det: list[str] = []
        self.ens: list[str] = []
        self.obs: list[int] = []

    def ingest_det(self, run: datetime, domains: list, steps: list[int], model: str = "ifs") -> dict[str, dict[str, Any]]:
        self.det.append(f"{run:%Y%m%d%H}" if model == "ifs" else f"{model}:{run:%Y%m%d%H}")
        if self.fail:
            raise FetchError("data.ecmwf.int unreachable")
        for d in domains:
            _manifest((self.root if model == "ifs" else self.root / model) / d.name / f"{run:%Y%m%d%H}", self.status)
        return {d.name: {"status": self.status} for d in domains}

    def ingest_ens(self, run: datetime, domain: Any, steps: list[int], members: list[int]) -> dict[str, Any]:
        self.ens.append(f"{run:%Y%m%d%H}")
        _manifest(self.root / domain.name / "ens" / f"{run:%Y%m%d%H}", "complete")
        return {"status": "complete"}

    def ingest_obs(self, domain: Any, hours: int, now: datetime) -> dict[str, Any]:
        self.obs.append(hours)
        ObsStore(self.root, domain.name).write_status({"ingested_at": now.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return {"metars_added": 5}


def _auto(root: Path, rec: Recorder, published: set[str], clock: list[datetime], **cfg: Any) -> AutoIngest:
    config = AutoConfig(domains=[DOMAIN], **cfg)
    return AutoIngest(root, config, ProbeFetcher(published), rec.ingest_det, rec.ingest_ens, rec.ingest_obs,
                      clock=lambda: clock[0])


def test_candidate_runs_and_probing() -> None:
    runs = candidate_runs(NOW, (0, 12), 4)
    assert [f"{r:%d%H}" for r in runs] == ["2612", "2600", "2512", "2500"]
    fetcher = ProbeFetcher({step_urls(runs[1], 72)[1]})
    assert latest_published(fetcher, runs, 72, step_urls) == runs[1]  # 12Z not published yet at 15 UTC
    assert len(fetcher.probes) == 2
    assert latest_published(ProbeFetcher(set()), runs, 72, step_urls) is None


def test_a_published_run_is_ingested_once(tmp_path: Path) -> None:
    rec, clock = Recorder(tmp_path), [NOW]
    auto = _auto(tmp_path, rec, {step_urls(datetime(2026, 9, 26, tzinfo=UTC), 72)[1]}, clock)
    report = auto.tick()
    assert rec.det == ["2026092600"] and report["done"]["deterministic"]["status"] == {"fixture": "complete"}
    clock[0] = NOW + timedelta(hours=3)
    auto.fetcher.probes.clear()
    auto.tick()
    assert rec.det == ["2026092600"]  # complete: never downloaded again
    assert auto.fetcher.probes == [step_urls(datetime(2026, 9, 26, 12, tzinfo=UTC), 72)[1]]  # only newer runs probed
    status = json.loads((tmp_path / ".auto" / "status.json").read_text())
    assert status["max_age_days"] == 7 and status["ens"] is False


def test_partial_or_failed_runs_are_retried_after_an_hour_not_before(tmp_path: Path) -> None:
    published = {step_urls(datetime(2026, 9, 26, tzinfo=UTC), 72)[1]}
    rec, clock = Recorder(tmp_path, status="partial"), [NOW]
    auto = _auto(tmp_path, rec, published, clock)
    auto.tick()
    clock[0] = NOW + timedelta(minutes=30)
    auto.tick()
    assert rec.det == ["2026092600"]
    clock[0] = NOW + timedelta(minutes=61)
    auto.tick()
    assert rec.det == ["2026092600", "2026092600"]

    failing = Recorder(tmp_path / "f", fail=True)
    auto = _auto(tmp_path / "f", failing, published, clock)
    report = auto.tick()
    assert "unreachable" in report["errors"]["deterministic"]
    assert failing.obs and "retention" not in report["errors"]  # other tasks still ran


def test_observation_cadence_and_history(tmp_path: Path) -> None:
    rec, clock = Recorder(tmp_path), [NOW]
    auto = _auto(tmp_path, rec, set(), clock)
    assert auto.obs_hours(DOMAIN, NOW) == 72  # first ingestion: backfill
    auto.tick()
    assert rec.obs == [72]
    clock[0] = NOW + timedelta(minutes=10)
    auto.tick()
    assert rec.obs == [72]  # last ingestion 10 min ago (< 30 min)
    assert auto.obs_hours(DOMAIN, NOW + timedelta(hours=5)) == 6
    assert auto.obs_hours(DOMAIN, NOW + timedelta(days=30)) == 168  # AWC API limit


def test_ensemble_is_opt_in(tmp_path: Path) -> None:
    run = datetime(2026, 9, 26, tzinfo=UTC)
    published = {step_urls(run, 72)[1], ens_step_urls(run, 24)[1]}
    rec = Recorder(tmp_path)
    _auto(tmp_path, rec, published, [NOW]).tick()
    assert rec.ens == []
    rec = Recorder(tmp_path / "e")
    auto = _auto(tmp_path / "e", rec, published, [NOW], ens=True)
    auto.tick()
    auto.tick()
    assert rec.ens == ["2026092600"]


def _old(path: Path, age: timedelta) -> None:
    t = (NOW - age).timestamp()
    os.utime(path, (t, t))


def test_age_retention_deletes_after_a_week_but_keeps_the_newest_run(tmp_path: Path) -> None:
    for run in ("2026091800", "2026091912", "2026092000", "2026092600"):
        _manifest(tmp_path / "fixture" / run, "complete")
    _manifest(tmp_path / "fixture" / "ens" / "2026091500", "complete")
    _manifest(tmp_path / "fixture" / "ens" / "2026092500", "complete")
    stale = tmp_path / "fixture" / "2026091000.tmp"
    stale.mkdir()
    _old(stale, timedelta(days=2))
    fresh_tmp = tmp_path / "fixture" / "2026092612.tmp"
    fresh_tmp.mkdir()  # an ingestion in progress
    metar = tmp_path / ".obs" / "fixture" / "metar"
    metar.mkdir(parents=True)
    for day in ("2026-09-18", "2026-09-19", "2026-09-26"):
        (metar / f"{day}.jsonl").write_text("")
    removed = apply_age_retention(tmp_path, [DOMAIN], timedelta(days=7), NOW)
    assert sorted(removed["fixture/runs"]) == ["2026091000.tmp", "2026091800", "2026091912"]  # limit 19/09 15:07
    assert removed["fixture/ens"] == ["2026091500"]
    assert removed["fixture/obs"] == ["metar/2026-09-18.jsonl"]
    assert sorted(p.name for p in (tmp_path / "fixture").iterdir()) == ["2026092000", "2026092600", "2026092612.tmp", "ens"]

    lonely = tmp_path / "lonely"
    _manifest(lonely / "fixture" / "2026080100", "complete")
    assert apply_age_retention(lonely, [DOMAIN], timedelta(days=7), NOW) == {}  # offline for weeks: data kept


def test_a_second_instance_is_refused(tmp_path: Path) -> None:
    first = InstanceLock(tmp_path)
    assert first.acquire() is True
    assert InstanceLock(tmp_path).acquire() is False


def test_command_line_validation() -> None:
    parser = build_parser()
    config = config_from_args(parser.parse_args([]))  # the repository's domains file
    assert config.run_hours == (0, 12) and config.max_age == timedelta(days=7) and config.ens is False
    with pytest.raises(ValueError, match="run hours"):
        config_from_args(parser.parse_args(["--run-hours", "3"]))
    with pytest.raises(ValueError, match="max-age-days"):
        config_from_args(parser.parse_args(["--max-age-days", "0"]))


def test_web_auto_starts_and_stops_the_downloader(monkeypatch: pytest.MonkeyPatch) -> None:
    import acf.web.awci_app as app

    started: list[list[str]] = []

    class Child:
        def __init__(self, cmd: list[str], **kwargs: Any) -> None:
            started.append(cmd)
            self.terminated = False

        def terminate(self) -> None:
            self.terminated = True

        def wait(self, timeout: float) -> int:
            return 0

    served: list[tuple[str, int]] = []
    monkeypatch.setattr(subprocess, "Popen", Child)
    monkeypatch.setattr(app, "run", lambda host, port: served.append((host, port)))
    assert app.main(["--auto", "--ens", "--port", "8095"]) == 0
    assert served == [("127.0.0.1", 8095)]
    assert started[0][1:] == ["-m", "acf.awci.ops.auto", "--parent-pid", str(os.getpid()), "--ens"]
    with pytest.raises(SystemExit):
        app.main(["--ens"])  # auto options without --auto
    with pytest.raises(SystemExit):
        app.main(["--auto", "--data-dir", "/x"])


def test_the_downloader_stops_when_its_parent_is_gone() -> None:
    gone = subprocess.Popen(["true"])
    gone.wait()
    assert wait(30, gone.pid, slice_s=0.01) is False  # returns at once, not after 30 s
    assert wait(0.02, None, slice_s=0.01) is True
    assert wait(0.02, os.getppid(), slice_s=0.01) is True  # our own parent is alive


def test_gfs_is_followed_on_request_into_its_own_directory(tmp_path: Path) -> None:
    run = datetime(2026, 9, 26, tzinfo=UTC)
    published = {step_urls(run, 72)[1], gfs_step_urls(run, 72)[1]}
    rec = Recorder(tmp_path)
    _auto(tmp_path, rec, published, [NOW]).tick()
    assert rec.det == ["2026092600"]  # GFS is opt-in
    rec = Recorder(tmp_path / "g")
    auto = _auto(tmp_path / "g", rec, published, [NOW], gfs=True)
    report = auto.tick()
    auto.tick()
    assert rec.det == ["2026092600", "gfs:2026092600"] and report["done"]["gfs"]["run"] == "2026092600"
    assert (tmp_path / "g" / "gfs" / "fixture" / "2026092600" / "manifest.json").exists()


def test_age_retention_also_prunes_gfs(tmp_path: Path) -> None:
    for run in ("2026091800", "2026092600"):
        _manifest(tmp_path / "gfs" / "fixture" / run, "complete")
    assert apply_age_retention(tmp_path, [DOMAIN], timedelta(days=7), NOW)["fixture/gfs"] == ["2026091800"]


def test_soundings_are_opt_in_and_follow_the_nominal_times(tmp_path: Path) -> None:
    calls: list[tuple[int, datetime]] = []

    def ingest_soundings(domain: Any, hours: int, now: datetime) -> dict[str, Any]:
        calls.append((hours, now))
        from acf.awci.obs.ingest import sounding_times

        ObsStore(tmp_path, domain.name).write_sounding_status(
            {"last_nominal": f"{sounding_times(now, hours)[-1]:%Y-%m-%dT%H:%M:%SZ}"})
        return {"soundings_added": 3, "missing": 1, "errors": 0}

    rec, clock = Recorder(tmp_path), [NOW]  # 26 Sept 15:07 UTC: the 12 UTC soundings are published (2 h delay)
    AutoIngest(tmp_path, AutoConfig(domains=[DOMAIN]), ProbeFetcher(set()), rec.ingest_det, rec.ingest_ens,
               rec.ingest_obs, clock=lambda: clock[0], ingest_soundings=ingest_soundings).tick()
    assert calls == []  # opt-in
    auto = AutoIngest(tmp_path, AutoConfig(domains=[DOMAIN], soundings=True), ProbeFetcher(set()), rec.ingest_det,
                      rec.ingest_ens, rec.ingest_obs, clock=lambda: clock[0], ingest_soundings=ingest_soundings)
    report = auto.tick()
    assert calls == [(48, NOW)] and report["done"]["soundings"]["fixture"]["soundings_added"] == 3
    assert ObsStore(tmp_path, DOMAIN.name).sounding_status()["last_nominal"] == "2026-09-26T12:00:00Z"
    assert auto.sounding_hours(DOMAIN, datetime(2026, 9, 27, 1, 50, tzinfo=UTC)) is None  # 27/00 not yet published
    calls.clear()
    clock[0] = datetime(2026, 9, 27, 2, 10, tzinfo=UTC)  # 27/00 published: since 26/12 (14 h 10) plus the previous time
    auto.tick()
    assert calls == [(15 + 12, clock[0])]
    assert json.loads((tmp_path / ".auto" / "status.json").read_text())["soundings"] is True


def test_failed_sounding_ingestion_is_retried_after_an_hour(tmp_path: Path) -> None:
    calls: list[datetime] = []

    def down(domain: Any, hours: int, now: datetime) -> dict[str, Any]:
        calls.append(now)
        raise RuntimeError("weather.uwyo.edu unreachable")

    rec, clock = Recorder(tmp_path), [NOW]
    auto = AutoIngest(tmp_path, AutoConfig(domains=[DOMAIN], soundings=True), ProbeFetcher(set()), rec.ingest_det,
                      rec.ingest_ens, rec.ingest_obs, clock=lambda: clock[0], ingest_soundings=down)
    assert "unreachable" in auto.tick()["errors"]["soundings"]
    clock[0] = NOW + timedelta(minutes=15)
    auto.tick()
    clock[0] = NOW + timedelta(minutes=61)
    auto.tick()
    assert calls == [NOW, NOW + timedelta(minutes=61)]
    assert config_from_args(build_parser().parse_args(["--soundings"])).soundings is True


def test_the_web_module_runs_with_python_dash_m() -> None:
    result = subprocess.run([sys.executable, "-m", "acf.web.awci_app", "--help"], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and "--auto" in result.stdout
