"""
ECMWF IFS 0.25 deg Open Data source (CC-BY-4.0, attribution "© ECMWF, CC-BY-4.0").

Layout: {BASE_URL}/{YYYYMMDD}/{HH}z/ifs/0p25/oper/{YYYYMMDDHH0000}-{step}h-oper-fc.{grib2,index}
The .index file is JSON-lines with param/levtype/levelist/_offset/_length; only the
needed messages are downloaded with HTTP Range requests (stdlib urllib, no new dependency).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

BASE_URL = "https://data.ecmwf.int/forecasts"
PL_PARAMS: tuple[str, ...] = ("t", "q", "r", "u", "v", "w", "gh", "d")
PL_LEVELS: tuple[int, ...] = (1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100)
SFC_PARAMS: tuple[str, ...] = (
    "2t", "2d", "10u", "10v", "10fg", "sp", "msl", "mucape", "tprate", "ptype", "tcc", "lsm",
    "tcw", "tcwv", "ttr", "sf", "sd", "rsn", "tp",  # SP1C: clouds, OLR, snow, freezing precipitation
)
RUN_HOURS = (0, 6, 12, 18)
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"


class FetchError(RuntimeError):
    """A URL could not be fetched after all retries."""


class MissingFieldsError(RuntimeError):
    """The index lacks required (param, level) messages."""


@dataclass(frozen=True)
class IndexEntry:
    param: str
    levtype: str
    level: int | None
    offset: int
    length: int


class Fetcher(Protocol):
    def get_text(self, url: str) -> str: ...

    def get_range(self, url: str, offset: int, length: int) -> bytes: ...


class UrllibFetcher:
    def __init__(
        self,
        timeout_s: float = 60.0,
        backoff_s: Sequence[float] = (2, 4, 8, 16),
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.timeout_s = timeout_s
        self.backoff_s = tuple(backoff_s)
        self.sleep = sleep

    def _get(self, url: str, headers: dict[str, str], expected_length: int | None = None) -> bytes:
        last_error: Exception | None = None
        for attempt in range(len(self.backoff_s) + 1):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    data = response.read()
                if expected_length is not None and len(data) != expected_length:
                    raise FetchError(f"{url}: got {len(data)} bytes, index announced {expected_length}")
                return data
            except (OSError, urllib.error.URLError, FetchError) as exc:
                last_error = exc
                if attempt < len(self.backoff_s):
                    self.sleep(self.backoff_s[attempt])
        raise FetchError(f"{url}: {last_error}")

    def get_text(self, url: str) -> str:
        return self._get(url, {}).decode("utf-8")

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        return self._get(url, {"Range": f"bytes={offset}-{offset + length - 1}"}, expected_length=length)


def step_urls(run: datetime, step: int) -> tuple[str, str]:
    stem = f"{BASE_URL}/{run:%Y%m%d}/{run:%H}z/ifs/0p25/oper/{run:%Y%m%d%H}0000-{step}h-oper-fc"
    return f"{stem}.grib2", f"{stem}.index"


def parse_index(text: str) -> list[IndexEntry]:
    entries = []
    for line in text.splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        level = raw.get("levelist")
        entries.append(IndexEntry(raw["param"], raw.get("levtype", ""), int(level) if level is not None else None,
                                  int(raw["_offset"]), int(raw["_length"])))
    return entries


def select_entries(entries: list[IndexEntry]) -> list[IndexEntry]:
    wanted = {(p, lev) for p in PL_PARAMS for lev in PL_LEVELS} | {(p, None) for p in SFC_PARAMS}
    chosen = {}
    for entry in entries:
        key = (entry.param, entry.level if entry.levtype == "pl" else None)
        if key in wanted and key not in chosen:
            chosen[key] = entry
    missing = sorted(wanted - chosen.keys(), key=str)
    if missing:
        raise MissingFieldsError(f"index lacks {missing}")
    return sorted(chosen.values(), key=lambda e: e.offset)


def fetch_step_messages(fetcher: Fetcher, run: datetime, step: int, max_workers: int = 8) -> list[bytes]:
    grib_url, index_url = step_urls(run, step)
    entries = select_entries(parse_index(fetcher.get_text(index_url)))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(lambda e: fetcher.get_range(grib_url, e.offset, e.length), entries))


def find_latest_run(fetcher: Fetcher, now: datetime, last_step: int, max_lookback_runs: int = 8) -> datetime:
    run = now.replace(minute=0, second=0, microsecond=0)
    run = run.replace(hour=max(h for h in RUN_HOURS if h <= run.hour))
    for _ in range(max_lookback_runs):
        try:
            fetcher.get_text(step_urls(run, last_step)[1])
            return run
        except FetchError:
            run -= timedelta(hours=6)
    raise FetchError(f"no run with step {last_step} published in the last {max_lookback_runs} runs")
