"""
acf-awci-auto: automatic download of the real data AWCI Web needs, and deletion after a week.

    acf-awci-auto [--domain NAME|all] [--run-hours 0,12] [--steps 0-72/3] [--obs-every-min 30]
                  [--gfs] [--soundings] [--ens] [--ens-run-hours 0] [--ens-steps 0-24/6] [--ens-members 1-50]
                  [--max-age-days 7] [--check-every-min 15] [--data-dir DIR] [--once]

Every `check-every-min` minutes, one pass:
1. observations (AWC METAR, TAF, SIGMET) when the last ingestion is older than `obs-every-min`; the METAR
   history fetched covers the time since the last ingestion (72 h the first time, at most 168 h);
2. the deterministic IFS run: the most recent run among `run-hours` whose last step is published on
   data.ecmwf.int (probed, never guessed from a timetable) is ingested unless already complete; a partial
   run is retried after `retry` (1 h), a run that failed likewise;
3. with `--gfs` (SP6), the NOAA GFS 0.25° run by the same rule, stored in <data>/gfs;
4. the IFS ENS run (opt-in `--ens`: about 19 GB downloaded per run for +0..+24 h / 6 h), same rule;
5. with `--soundings` (SP7), radiosondes (University of Wyoming) once a new 00/12 UTC sounding time is
   published (2 h after it): the time since the last ingestion plus the previous nominal time, whose stations
   that were still missing are asked once more; archived profiles are never requested again;
6. deletion of everything older than `max-age-days`: IFS, GFS and ENS runs whose run time is older,
   METAR/SIGMET/sounding day files, and abandoned temporary directories (`<run>.tmp`, `<run>.old` untouched for a
   day). The most recent run of each kind is kept whatever its age, so that the dashboard is never emptied
   by a machine that stayed offline for a week.

Each task is isolated: an unreachable source is logged and retried at the next pass, the loop never stops on
it. A lock file in the data directory prevents two instances. The last pass is written to
`<data>/.auto/status.json`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, TextIO

from loguru import logger

from acf.awci.obs.store import ObsStore, parse_time
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, Domain, load_domains
from acf.awci.ops.ens_store import ens_dir
from acf.awci.ops.ingest import parse_steps
from acf.awci.ops.source_ecmwf import RUN_HOURS, Fetcher, FetchError, ens_step_urls, step_urls
from acf.awci.ops.source_gfs import gfs_step_urls
from acf.awci.ops.store import data_root, model_root, run_id

STALE_TMP = timedelta(days=1)
FIRST_OBS_HOURS = 72
FIRST_SOUNDING_HOURS = 48
MAX_OBS_HOURS = 168  # AWC Data API limit (acf-awci-obs --hours)


@dataclass(frozen=True)
class AutoConfig:
    domains: list[Domain]
    steps: list[int] = field(default_factory=lambda: parse_steps("0-72/3"))
    run_hours: tuple[int, ...] = (0, 12)
    obs_every: timedelta = timedelta(minutes=30)
    ens: bool = False
    gfs: bool = False  # SP6: also follow NOAA GFS 0.25° (same run hours and steps), stored in <data>/gfs
    soundings: bool = False  # SP7: radiosondes from the University of Wyoming (academic service: opt-in)
    ens_steps: list[int] = field(default_factory=lambda: parse_steps("0-24/6"))
    ens_run_hours: tuple[int, ...] = (0,)
    ens_members: list[int] = field(default_factory=lambda: list(range(1, 51)))
    max_age: timedelta = timedelta(days=7)
    retry: timedelta = timedelta(hours=1)
    lookback_runs: int = 4

    def __post_init__(self) -> None:
        for hours in (self.run_hours, self.ens_run_hours):
            if not hours or any(h not in RUN_HOURS for h in hours):
                raise ValueError(f"run hours must be among {RUN_HOURS}, got {hours}")
        if self.max_age < timedelta(days=1):
            raise ValueError("max_age must be at least one day")


def candidate_runs(now: datetime, run_hours: tuple[int, ...], count: int) -> list[datetime]:
    """The `count` most recent run times at `run_hours` not later than `now`, newest first."""
    t = now.replace(minute=0, second=0, microsecond=0)
    out: list[datetime] = []
    while len(out) < count:
        if t.hour in run_hours:
            out.append(t)
        t -= timedelta(hours=1)
    return out


def latest_published(fetcher: Fetcher, candidates: list[datetime], last_step: int,
                     urls: Callable[[datetime, int], tuple[str, str]]) -> datetime | None:
    """First candidate whose index of the last step is published, None when none is."""
    for run in candidates:
        try:
            fetcher.get_text(urls(run, last_step)[1])
            return run
        except FetchError:
            continue
    return None


def _run_time(name: str) -> datetime | None:
    try:
        return datetime.strptime(name, "%Y%m%d%H").replace(tzinfo=UTC)
    except ValueError:
        return None


def _prune_runs(folder: Path, limit: datetime, now: datetime) -> list[str]:
    if not folder.exists():
        return []
    runs = sorted((t, p) for p in folder.iterdir() if p.is_dir() and (t := _run_time(p.name)) is not None)
    removed = []
    for t, path in runs[:-1]:  # the most recent run is always kept
        if t < limit:
            shutil.rmtree(path, ignore_errors=True)
            removed.append(path.name)
    for path in folder.iterdir():  # interrupted ingestions
        if path.is_dir() and path.suffix in (".tmp", ".old"):
            if now - datetime.fromtimestamp(path.stat().st_mtime, UTC) > STALE_TMP:
                shutil.rmtree(path, ignore_errors=True)
                removed.append(path.name)
    return removed


def apply_age_retention(root: Path, domains: list[Domain], max_age: timedelta, now: datetime) -> dict[str, list[str]]:
    """Delete the data older than `max_age` (run time for cubes, day for observations); see module doc."""
    limit = now - max_age
    removed: dict[str, list[str]] = {}
    for d in domains:
        removed[f"{d.name}/runs"] = _prune_runs(Path(root) / d.name, limit, now)
        removed[f"{d.name}/ens"] = _prune_runs(ens_dir(root, d.name), limit, now)
        removed[f"{d.name}/gfs"] = _prune_runs(model_root(Path(root), "gfs") / d.name, limit, now)
        removed[f"{d.name}/obs"] = ObsStore(root, d.name).apply_retention(max(1, max_age.days), now)
    return {k: v for k, v in removed.items() if v}


# Task callables (injected, so that the scheduling is tested without network): they raise on failure.
IngestDet = Callable[..., dict[str, dict[str, Any]]]  # (run, domains, steps, model="ifs") -> manifests per domain
IngestEns = Callable[[datetime, Domain, list[int], list[int]], dict[str, Any]]
IngestObs = Callable[[Domain, int, datetime], dict[str, Any]]
IngestSoundings = Callable[[Domain, int, datetime], dict[str, Any]]


class AutoIngest:
    def __init__(self, root: Path, config: AutoConfig, fetcher: Fetcher, ingest_det: IngestDet,
                 ingest_ens: IngestEns, ingest_obs: IngestObs,
                 clock: Callable[[], datetime] = lambda: datetime.now(UTC),
                 ingest_soundings: IngestSoundings | None = None) -> None:
        self.root, self.config, self.fetcher, self.clock = Path(root), config, fetcher, clock
        self.ingest_det, self.ingest_ens, self.ingest_obs = ingest_det, ingest_ens, ingest_obs
        self.ingest_soundings = ingest_soundings
        self.attempts: dict[str, datetime] = {}  # task key -> last attempt, for retries of incomplete runs

    # -- decisions ------------------------------------------------------------------------------------
    def _manifest(self, folder: Path) -> dict[str, Any] | None:
        path = folder / "manifest.json"
        return json.loads(path.read_text()) if path.exists() else None

    def _due(self, key: str, manifests: list[dict[str, Any] | None], now: datetime) -> bool:
        if manifests and all(m is not None and m.get("status") == "complete" for m in manifests):
            return False
        last = self.attempts.get(key)
        return last is None or now - last >= self.config.retry

    def obs_hours(self, domain: Domain, now: datetime) -> int | None:
        """METAR history to fetch now, None when the last ingestion is recent enough."""
        last = ObsStore(self.root, domain.name).status().get("ingested_at")
        if last is None:
            return FIRST_OBS_HOURS
        age = now - parse_time(last)
        if age < self.config.obs_every:
            return None
        return int(min(MAX_OBS_HOURS, max(3, math.ceil(age / timedelta(hours=1)) + 1)))

    def sounding_hours(self, domain: Domain, now: datetime) -> int | None:
        """Radiosonde history to request now, None until a new nominal time is published."""
        from acf.awci.obs.ingest import sounding_times

        published = sounding_times(now, 24)
        last = ObsStore(self.root, domain.name).sounding_status().get("last_nominal")
        if last is None:
            return FIRST_SOUNDING_HOURS
        if not published or published[-1] <= parse_time(last):
            return None
        return int(min(MAX_OBS_HOURS, math.ceil((now - parse_time(last)) / timedelta(hours=1)) + 12))

    # -- one pass -------------------------------------------------------------------------------------
    def _task(self, report: dict[str, Any], name: str, action: Callable[[], Any]) -> None:
        try:
            result = action()
            if result is not None:
                report["done"][name] = result
        except Exception as exc:  # noqa: BLE001 - a daemon pass must survive any failing source
            logger.error("AWCI auto {}: {}", name, exc)
            report["errors"][name] = f"{type(exc).__name__}: {exc}"

    def _newest_complete(self, folders: list[Path]) -> datetime | None:
        """Newest run complete in every folder: older runs are never probed again."""
        complete = None
        for folder in folders:
            runs = {t for p in folder.iterdir() if (t := _run_time(p.name)) is not None
                    and (self._manifest(p) or {}).get("status") == "complete"} if folder.exists() else set()
            complete = runs if complete is None else complete & runs
        return max(complete) if complete else None

    def _candidates(self, now: datetime, hours: tuple[int, ...], folders: list[Path]) -> list[datetime]:
        newest = self._newest_complete(folders)
        return [r for r in candidate_runs(now, hours, self.config.lookback_runs) if newest is None or r > newest]

    def _det(self, now: datetime, model: str = "ifs") -> Any:
        c = self.config
        root = model_root(self.root, model)
        candidates = self._candidates(now, c.run_hours, [root / d.name for d in c.domains])
        run = latest_published(self.fetcher, candidates, c.steps[-1], gfs_step_urls if model == "gfs" else step_urls)
        if run is None:
            return None
        key = f"{model}/{run_id(run)}"
        if not self._due(key, [self._manifest(root / d.name / run_id(run)) for d in c.domains], now):
            return None
        self.attempts[key] = now
        manifests = self.ingest_det(run, c.domains, c.steps, model=model) if model != "ifs" else \
            self.ingest_det(run, c.domains, c.steps)
        return {"run": run_id(run), "status": {name: m.get("status") for name, m in manifests.items()}}

    def _ens(self, now: datetime) -> Any:
        c = self.config
        candidates = self._candidates(now, c.ens_run_hours, [ens_dir(self.root, d.name) for d in c.domains])
        run = latest_published(self.fetcher, candidates, c.ens_steps[-1], ens_step_urls)
        if run is None:
            return None
        out = {}
        for d in c.domains:
            key = f"ens/{d.name}/{run_id(run)}"
            if self._due(key, [self._manifest(ens_dir(self.root, d.name) / run_id(run))], now):
                self.attempts[key] = now
                out[d.name] = self.ingest_ens(run, d, c.ens_steps, c.ens_members).get("status")
        return {"run": run_id(run), "status": out} if out else None

    def _obs(self, now: datetime) -> Any:
        out = {}
        for d in self.config.domains:
            hours = self.obs_hours(d, now)
            if hours is not None:
                result = self.ingest_obs(d, hours, now)
                out[d.name] = {"hours": hours, "metars_added": result.get("metars_added")}
        return out or None

    def _soundings(self, now: datetime) -> Any:
        if self.ingest_soundings is None:
            raise RuntimeError("no radiosonde ingestion configured")
        out = {}
        for d in self.config.domains:
            hours, key = self.sounding_hours(d, now), f"soundings/{d.name}"
            last = self.attempts.get(key)
            if hours is None or (last is not None and now - last < self.config.retry):
                continue
            self.attempts[key] = now
            result = self.ingest_soundings(d, hours, now)
            out[d.name] = {"hours": hours, "soundings_added": result.get("soundings_added"),
                           "missing": result.get("missing"), "errors": result.get("errors")}
        return out or None

    def tick(self) -> dict[str, Any]:
        now = self.clock()
        report: dict[str, Any] = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "done": {}, "errors": {}}
        self._task(report, "observations", lambda: self._obs(now))
        self._task(report, "deterministic", lambda: self._det(now))
        if self.config.gfs:
            self._task(report, "gfs", lambda: self._det(now, "gfs"))
        if self.config.ens:
            self._task(report, "ensemble", lambda: self._ens(now))
        if self.config.soundings:
            self._task(report, "soundings", lambda: self._soundings(now))
        self._task(report, "retention", lambda: apply_age_retention(self.root, self.config.domains,
                                                                      self.config.max_age, self.clock()) or None)
        status_dir = self.root / ".auto"
        status_dir.mkdir(parents=True, exist_ok=True)
        tmp = status_dir / "status.json.tmp"
        tmp.write_text(json.dumps(report | {"max_age_days": self.config.max_age.days, "ens": self.config.ens,
                                         "gfs": self.config.gfs, "soundings": self.config.soundings}, indent=1))
        os.replace(tmp, status_dir / "status.json")
        return report


class InstanceLock:
    """Exclusive lock on `<data>/.auto/lock`: a second acf-awci-auto on the same data exits (POSIX, WSL)."""

    def __init__(self, root: Path) -> None:
        self.path = Path(root) / ".auto" / "lock"
        self.handle: TextIO | None = None

    def acquire(self) -> bool:
        try:
            import fcntl
        except ImportError:  # native Windows: no advisory lock available, run unguarded
            return True
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("w")
        try:
            fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.handle.close()
            self.handle = None
            return False
        self.handle.write(str(os.getpid()))
        self.handle.flush()
        return True


def _real_soundings(root: Path) -> IngestSoundings:
    from acf.awci.obs.ingest import ingest_soundings
    from acf.awci.obs.sounding import IGRA_STATIONS_URL, UwyoClient

    def soundings(domain: Domain, hours: int, now: datetime) -> dict[str, Any]:
        return ingest_soundings(UwyoClient(), ObsStore(root, domain.name), domain, hours, now,
                                lambda: UwyoClient._http_get(IGRA_STATIONS_URL))

    return soundings


def _real_tasks(root: Path, connections: int, max_age: timedelta) -> tuple[Fetcher, IngestDet, IngestEns, IngestObs]:
    from acf.awci.obs.ingest import ingest_domain
    from acf.awci.obs.source_awc import AwcClient, UrllibAwcFetcher
    from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, load_cloud_profile
    from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
    from acf.awci.ops.ens_ingest import ingest_ens_run
    from acf.awci.ops.ingest import ingest_run
    from acf.awci.ops.source_ecmwf import UrllibFetcher

    fetcher = UrllibFetcher()

    def det(run: datetime, domains: list[Domain], steps: list[int], model: str = "ifs") -> dict[str, dict[str, Any]]:
        return ingest_run(run, domains, load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), fetcher, model_root(root, model),
                          steps, keep=None, cloud_profile=load_cloud_profile(DEFAULT_CLOUD_PROFILE_PATH), model=model)

    def ens(run: datetime, domain: Domain, steps: list[int], members: list[int]) -> dict[str, Any]:
        return ingest_ens_run(run, domain, fetcher, root, steps, members, connections=connections, keep=None)

    def obs(domain: Domain, hours: int, now: datetime) -> dict[str, Any]:
        return dict(ingest_domain(AwcClient(UrllibAwcFetcher()), ObsStore(root, domain.name), domain, hours, now,
                                  retention_days=max(1, max_age.days)))

    return fetcher, det, ens, obs


def parent_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:  # exists, owned by someone else
        return True
    return os.getppid() == pid


def wait(seconds: float, parent_pid: int | None, slice_s: float = 5.0) -> bool:
    """Sleep `seconds`; False as soon as the parent process (acf-awci-web --auto) has gone."""
    end = time.monotonic() + seconds
    while (left := end - time.monotonic()) > 0:
        if parent_pid is not None and not parent_alive(parent_pid):
            return False
        time.sleep(min(slice_s, left))
    return parent_pid is None or parent_alive(parent_pid)


def _hours(spec: str) -> tuple[int, ...]:
    return tuple(sorted({int(h) for h in spec.split(",") if h.strip()}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="acf-awci-auto", description=__doc__.splitlines()[1])
    parser.add_argument("--domain", default="all")
    parser.add_argument("--run-hours", default="0,12", help="deterministic runs to follow, among 0,6,12,18 (UTC)")
    parser.add_argument("--steps", default="0-72/3")
    parser.add_argument("--obs-every-min", type=int, default=30)
    parser.add_argument("--ens", action="store_true", help="also compute the IFS ENS (≈19 GB downloaded per run)")
    parser.add_argument("--gfs", action="store_true", help="also follow NOAA GFS 0.25° (second model, SP6)")
    parser.add_argument("--soundings", action="store_true",
                        help="also archive radiosondes (University of Wyoming, SP7) after 00 and 12 UTC")
    parser.add_argument("--ens-run-hours", default="0")
    parser.add_argument("--ens-steps", default="0-24/6")
    parser.add_argument("--ens-members", default="1-50")
    parser.add_argument("--connections", type=int, default=16)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--check-every-min", type=int, default=15)
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--once", action="store_true", help="one pass, then exit (for cron)")
    parser.add_argument("--parent-pid", type=int, default=None, help=argparse.SUPPRESS)  # set by acf-awci-web --auto
    return parser


def config_from_args(args: argparse.Namespace) -> AutoConfig:
    from acf.awci.ops.ens_ingest import parse_members

    all_domains = load_domains(args.domains_file)
    domains = list(all_domains.values()) if args.domain == "all" else [all_domains[args.domain]]
    if not 10 <= args.obs_every_min <= 180:
        raise ValueError("--obs-every-min must lie within 10-180")
    if not 5 <= args.check_every_min <= 120:
        raise ValueError("--check-every-min must lie within 5-120")
    if not 1 <= args.max_age_days <= 30:
        raise ValueError("--max-age-days must lie within 1-30")
    if not 1 <= args.connections <= 32:
        raise ValueError("--connections must lie within 1-32 (be fair to data.ecmwf.int)")
    return AutoConfig(domains=domains, steps=parse_steps(args.steps), run_hours=_hours(args.run_hours),
                      obs_every=timedelta(minutes=args.obs_every_min), ens=args.ens, gfs=args.gfs,
                      soundings=args.soundings,
                      ens_steps=parse_steps(args.ens_steps), ens_run_hours=_hours(args.ens_run_hours),
                      ens_members=parse_members(args.ens_members), max_age=timedelta(days=args.max_age_days))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = config_from_args(args)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    root = Path(args.data_dir) if args.data_dir else data_root()
    lock = InstanceLock(root)
    if not lock.acquire():
        logger.error("AWCI auto: another acf-awci-auto already runs on {}", root)
        return 1
    fetcher, det, ens, obs = _real_tasks(root, args.connections, config.max_age)
    auto = AutoIngest(root, config, fetcher, det, ens, obs, ingest_soundings=_real_soundings(root))
    logger.info("AWCI auto on {}: domains {}, runs {} UTC, ENS {}, deletion after {} days", root,
                [d.name for d in config.domains], config.run_hours, config.ens, config.max_age.days)
    try:
        while True:
            report = auto.tick()
            logger.info("AWCI auto pass: done {} errors {}", report["done"], report["errors"])
            if args.once:
                return 1 if report["errors"] else 0
            if not wait(args.check_every_min * 60, args.parent_pid):
                logger.info("AWCI auto: acf-awci-web stopped, stopping too")
                return 0
    except KeyboardInterrupt:
        logger.info("AWCI auto stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
