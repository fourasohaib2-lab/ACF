"""
Client of the NOAA/NWS Aviation Weather Center Data API (https://aviationweather.gov/data/api/).

Public-domain data (US Government). Every list endpoint returns at most `AWC_CAP` items (measured
2026-09-26: 400), so a request that comes back full is split, geographically for stations and by
station batch for METAR/TAF, until no answer is truncated. Every item is validated before use; invalid
ones are dropped and counted in `rejected`, never propagated.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from acf.awci.ops.domains import Domain

API = "https://aviationweather.gov/api/data"
AWC_CAP = 400
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"
MIN_TILE_DEG = 0.5
_ICAO = re.compile(r"^[A-Z][A-Z0-9]{3}$")
_HAZARDS = {"TS", "TURB", "ICE", "VA", "TC", "MTW"}


class AwcError(RuntimeError):
    """The AWC API did not return a usable answer."""


class AwcFetcher(Protocol):
    def get(self, url: str, timeout: float) -> bytes: ...


class UrllibAwcFetcher:
    def get(self, url: str, timeout: float) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()


@dataclass(frozen=True)
class Station:
    icao: str
    name: str
    lat: float
    lon: float
    elev_m: float
    metar: bool
    taf: bool

    def as_dict(self) -> dict[str, Any]:
        return {"icao": self.icao, "name": self.name, "lat": self.lat, "lon": self.lon, "elev_m": self.elev_m,
                "metar": self.metar, "taf": self.taf}


def iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(value: Any, low: float, high: float) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if low <= value <= high else None


def _text(value: Any, limit: int = 4000) -> str | None:
    return value if isinstance(value, str) and 0 < len(value) <= limit else None


class AwcClient:
    def __init__(self, fetcher: AwcFetcher, timeout_s: float = 20.0, batch: int = 60) -> None:
        self.fetcher, self.timeout_s, self.batch = fetcher, timeout_s, batch
        self.rejected = 0

    def _get(self, endpoint: str, **params: str) -> list[Any]:
        url = f"{API}/{endpoint}?{urllib.parse.urlencode({**params, 'format': 'json'})}"
        try:
            body = self.fetcher.get(url, self.timeout_s)
        except OSError as exc:
            raise AwcError(f"AWC {endpoint} unavailable: {exc}") from exc
        if not body.strip():
            return []  # the API answers 204 / empty body when nothing matches
        try:
            payload = json.loads(body)
        except ValueError as exc:
            raise AwcError(f"AWC {endpoint} answered non-JSON content") from exc
        if not isinstance(payload, list):
            raise AwcError(f"AWC {endpoint} answered {type(payload).__name__} instead of a list")
        return payload

    # -- stations -------------------------------------------------------------------------------------
    def _station(self, raw: Any) -> Station | None:
        if not isinstance(raw, dict):
            return None
        icao, lat, lon = raw.get("icaoId"), _num(raw.get("lat"), -90, 90), _num(raw.get("lon"), -180, 180)
        elev = _num(raw.get("elev"), -500, 9000)
        site_type = raw.get("siteType")
        kinds: list[Any] = site_type if isinstance(site_type, list) else []
        if not (isinstance(icao, str) and _ICAO.match(icao)) or lat is None or lon is None or elev is None:
            return None
        return Station(icao, _text(raw.get("site"), 200) or icao, lat, lon, elev, "METAR" in kinds, "TAF" in kinds)

    def _tile(self, s: float, w: float, n: float, e: float, out: dict[str, Station]) -> None:
        items = self._get("stationinfo", bbox=f"{s:g},{w:g},{n:g},{e:g}")
        if len(items) >= AWC_CAP and (n - s) > MIN_TILE_DEG:
            ms, mw = (s + n) / 2, (w + e) / 2
            for box in ((s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)):
                self._tile(*box, out)
            return
        for raw in items:
            station = self._station(raw)
            if station is None:
                if not (isinstance(raw, dict) and raw.get("icaoId") is None):  # buoys have no ICAO id
                    self.rejected += 1
                continue
            if station.metar and s <= station.lat <= n and w <= station.lon <= e:
                out[station.icao] = station

    def stations(self, domain: Domain) -> list[Station]:
        """METAR stations inside the domain (tiles are split while an answer is capped)."""
        found: dict[str, Station] = {}
        self._tile(domain.south, domain.west, domain.north, domain.east, found)
        return sorted(found.values(), key=lambda st: st.icao)

    # -- METAR / TAF ----------------------------------------------------------------------------------
    def _batched(self, endpoint: str, ids: list[str], parse: Any, **params: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        pending = [ids[i:i + self.batch] for i in range(0, len(ids), self.batch)]
        while pending:
            chunk = pending.pop()
            items = self._get(endpoint, ids=",".join(chunk), **params)
            if len(items) >= AWC_CAP and len(chunk) > 1:
                half = len(chunk) // 2
                pending += [chunk[:half], chunk[half:]]
                continue
            for raw in items:
                record = parse(raw)
                if record is None:
                    self.rejected += 1
                else:
                    out.append(record)
        return out

    @staticmethod
    def _metar(raw: Any) -> dict[str, Any] | None:
        if not isinstance(raw, dict):
            return None
        icao, text = raw.get("icaoId"), _text(raw.get("rawOb"), 1000)
        t = _num(raw.get("obsTime"), 0, 4.1e9)
        if not (isinstance(icao, str) and _ICAO.match(icao)) or text is None or t is None:
            return None
        if not text.startswith(("METAR", "SPECI")):
            text = f"{raw.get('metarType') if raw.get('metarType') in ('METAR', 'SPECI') else 'METAR'} {text}"
        return {"icao": icao, "obs_time": iso(t), "raw": text, "kind": text.split()[0],
                "lat": _num(raw.get("lat"), -90, 90), "lon": _num(raw.get("lon"), -180, 180),
                "elev_m": _num(raw.get("elev"), -500, 9000)}

    def metars(self, ids: Iterable[str], hours: int) -> list[dict[str, Any]]:
        return self._batched("metar", sorted(set(ids)), self._metar, hours=str(int(hours)))

    @staticmethod
    def _taf(raw: Any) -> dict[str, Any] | None:
        if not isinstance(raw, dict):
            return None
        icao, text = raw.get("icaoId"), _text(raw.get("rawTAF"))
        issued, v0, v1 = (_num(raw.get(k), 0, 4.1e9) for k in ("issueTime", "validTimeFrom", "validTimeTo"))
        if isinstance(raw.get("issueTime"), str):
            issued = datetime.fromisoformat(raw["issueTime"].replace("Z", "+00:00")).timestamp()
        if not (isinstance(icao, str) and _ICAO.match(icao)) or text is None or v0 is None or v1 is None:
            return None
        periods = []
        for f in raw.get("fcsts") or []:
            if not isinstance(f, dict) or _num(f.get("timeFrom"), 0, 4.1e9) is None:
                continue
            clouds = [{"cover": c.get("cover"), "base_ft": c.get("base"), "type": c.get("type")}
                      for c in f.get("clouds") or [] if isinstance(c, dict)]
            periods.append({"from": iso(f["timeFrom"]), "to": iso(f["timeTo"]) if _num(f.get("timeTo"), 0, 4.1e9) else None,
                            "change": _text(f.get("fcstChange"), 10), "probability": _num(f.get("probability"), 0, 100),
                            "visibility": f.get("visib") if isinstance(f.get("visib"), (str, int, float)) else None,
                            "weather": _text(f.get("wxString"), 100), "clouds": clouds})
        return {"icao": icao, "issued": iso(issued) if issued else None, "valid_from": iso(v0), "valid_to": iso(v1),
                "raw": text, "periods": periods}

    def tafs(self, ids: Iterable[str]) -> list[dict[str, Any]]:
        return self._batched("taf", sorted(set(ids)), self._taf)

    # -- SIGMET ---------------------------------------------------------------------------------------
    @staticmethod
    def _sigmet(raw: Any) -> dict[str, Any] | None:
        if not isinstance(raw, dict) or raw.get("hazard") not in _HAZARDS:
            return None
        text = _text(raw.get("rawSigmet"))
        v0, v1 = _num(raw.get("validTimeFrom"), 0, 4.1e9), _num(raw.get("validTimeTo"), 0, 4.1e9)
        coords = []
        for c in raw.get("coords") or []:
            lat, lon = (_num(c.get("lat"), -90, 90), _num(c.get("lon"), -180, 180)) if isinstance(c, dict) else (None, None)
            if lat is None or lon is None:
                return None
            coords.append([lon, lat])
        if text is None or v0 is None or v1 is None or len(coords) < 3:
            return None
        received = raw.get("receiptTime") if isinstance(raw.get("receiptTime"), str) else None
        return {"hazard": raw["hazard"], "qualifier": _text(raw.get("qualifier"), 40), "fir": _text(raw.get("firId"), 8),
                "fir_name": _text(raw.get("firName"), 100), "series": _text(raw.get("seriesId"), 8),
                "base_ft": _num(raw.get("base"), 0, 100000), "top_ft": _num(raw.get("top"), 0, 100000),
                "valid_from": iso(v0), "valid_to": iso(v1), "received": received,
                "direction": _text(raw.get("dir"), 4), "speed_kt": _text(str(raw["spd"]), 4) if raw.get("spd") else None,
                "change": _text(raw.get("chng"), 4), "coords": coords, "raw": text}

    def isigmets(self, domain: Domain) -> list[dict[str, Any]]:
        """International SIGMETs whose polygon bounding box crosses the domain."""
        out = []
        for raw in self._get("isigmet"):
            record = self._sigmet(raw)
            if record is None:
                self.rejected += 1
                continue
            lons = [c[0] for c in record["coords"]]
            lats = [c[1] for c in record["coords"]]
            if max(lats) >= domain.south and min(lats) <= domain.north and max(lons) >= domain.west \
                    and min(lons) <= domain.east:
                out.append(record)
        return out
