"""
On-disk store of aeronautical observations per domain: `{data}/.obs/{domain}/`.

- `stations.json`: METAR stations of the domain (`fetched_at` + list);
- `metar/YYYY-MM-DD.jsonl`: METAR/SPECI by UTC day of observation, unique (station, time, text);
- `taf/latest.json`: latest TAF per station;
- `sigmet/YYYY-MM-DD.jsonl`: SIGMETs by UTC day of their validity start, unique by text;
- `status.json`: last ingestion time and counts.

Every file is written to a temporary name and renamed (readers never see a partial file).
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

_DAY_FILE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.jsonl$")


def parse_time(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(text)
    os.replace(tmp, path)


def _read_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class ObsStore:
    def __init__(self, data_dir: Path | str, domain: str) -> None:
        self.root = Path(data_dir) / ".obs" / domain

    # -- stations -------------------------------------------------------------------------------------
    def write_stations(self, stations: list[dict[str, Any]], now: datetime) -> None:
        payload = {"fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "stations": stations}
        _write(self.root / "stations.json", json.dumps(payload))

    def stations_fetched_at_of(self, name: str) -> datetime | None:
        path = self.root / name
        return parse_time(json.loads(path.read_text())["fetched_at"]) if path.exists() else None

    def stations_fetched_at(self) -> datetime | None:
        path = self.root / "stations.json"
        return parse_time(json.loads(path.read_text())["fetched_at"]) if path.exists() else None

    def stations(self) -> list[dict[str, Any]]:
        path = self.root / "stations.json"
        return json.loads(path.read_text())["stations"] if path.exists() else []

    # -- day-partitioned archives ---------------------------------------------------------------------
    def _add(self, kind: str, records: list[dict[str, Any]], time_key: str, identity: Any) -> int:
        by_day: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            by_day.setdefault(parse_time(record[time_key]).strftime("%Y-%m-%d"), []).append(record)
        added = 0
        for day, new in by_day.items():
            path = self.root / kind / f"{day}.jsonl"
            existing = _read_lines(path)
            keys = {identity(r) for r in existing}
            fresh = []
            for record in new:
                if identity(record) not in keys:
                    keys.add(identity(record))
                    fresh.append(record)
            if fresh:
                merged = sorted(existing + fresh, key=lambda r: (r[time_key], json.dumps(r, sort_keys=True)))
                _write(path, "".join(json.dumps(r) + "\n" for r in merged))
                added += len(fresh)
        return added

    def _between(self, kind: str, time_key: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        day: date = start.date()
        while day <= end.date():
            for record in _read_lines(self.root / kind / f"{day:%Y-%m-%d}.jsonl"):
                if start <= parse_time(record[time_key]) <= end:
                    out.append(record)
            day += timedelta(days=1)
        return out

    def add_metars(self, records: list[dict[str, Any]]) -> int:
        return self._add("metar", records, "obs_time", lambda r: (r["icao"], r["obs_time"], r["raw"]))

    def metars(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """METAR/SPECI observed in [start, end], sorted by time."""
        return self._between("metar", "obs_time", start, end)

    def add_soundings(self, records: list[dict[str, Any]]) -> int:
        """Radiosonde profiles (SP7), one record per station and nominal time (00/12 UTC)."""
        return self._add("sounding", records, "nominal_time", lambda r: (r["wmo"], r["nominal_time"]))

    def soundings(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        return self._between("sounding", "nominal_time", start, end)

    def write_sounding_stations(self, stations: list[dict[str, Any]], now: datetime) -> None:
        _write(self.root / "sounding_stations.json",
               json.dumps({"fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "stations": stations}))

    def sounding_stations(self) -> list[dict[str, Any]]:
        path = self.root / "sounding_stations.json"
        return list(json.loads(path.read_text())["stations"]) if path.exists() else []

    def write_sounding_status(self, status: dict[str, Any]) -> None:
        _write(self.root / "sounding_status.json", json.dumps(status))

    def sounding_status(self) -> dict[str, Any]:
        """Last radiosonde ingestion: ingested_at and last_nominal (latest nominal time requested)."""
        path = self.root / "sounding_status.json"
        return json.loads(path.read_text()) if path.exists() else {}

    def add_sigmets(self, records: list[dict[str, Any]]) -> int:
        return self._add("sigmet", records, "valid_from", lambda r: r["raw"])

    def sigmets_at(self, when: datetime, max_validity_h: int = 24) -> list[dict[str, Any]]:
        """SIGMETs valid at `when` (validity start inclusive, end exclusive)."""
        candidates = self._between("sigmet", "valid_from", when - timedelta(hours=max_validity_h), when)
        return [s for s in candidates if parse_time(s["valid_from"]) <= when < parse_time(s["valid_to"])]

    # -- TAF, status ----------------------------------------------------------------------------------
    def write_tafs(self, tafs: list[dict[str, Any]]) -> None:
        latest: dict[str, dict[str, Any]] = {}
        for taf in tafs:
            if taf["icao"] not in latest or (taf.get("issued") or "") > (latest[taf["icao"]].get("issued") or ""):
                latest[taf["icao"]] = taf
        _write(self.root / "taf" / "latest.json", json.dumps(sorted(latest.values(), key=lambda t: t["icao"])))

    def tafs(self) -> list[dict[str, Any]]:
        path = self.root / "taf" / "latest.json"
        return json.loads(path.read_text()) if path.exists() else []

    def write_status(self, status: dict[str, Any]) -> None:
        _write(self.root / "status.json", json.dumps(status))

    def status(self) -> dict[str, Any]:
        path = self.root / "status.json"
        return json.loads(path.read_text()) if path.exists() else {}

    def mtime(self) -> float:
        """Latest modification time of the archives (cache key for derived results)."""
        files = [p for p in self.root.rglob("*") if p.is_file()] if self.root.exists() else []
        return max((p.stat().st_mtime for p in files), default=0.0)

    def apply_retention(self, days: int, now: datetime) -> list[str]:
        """Delete day files older than `days` days; returns their paths relative to the store."""
        limit = (now - timedelta(days=days)).date()
        removed = []
        for kind in ("metar", "sigmet", "sounding"):
            folder = self.root / kind
            for path in sorted(folder.glob("*.jsonl")) if folder.exists() else []:
                match = _DAY_FILE.match(path.name)
                if match and date.fromisoformat(match.group(1)) < limit:
                    path.unlink()
                    removed.append(f"{kind}/{path.name}")
        return removed
