"""
Radiosonde profiles for the AWCI verification (spec SP7 §2).

- Stations: IGRA v2 station list (NOAA NCEI, igra2-station-list.txt, fixed-width: ID 1-11, LAT 13-20, LON 22-30,
  ELEV 32-37, STATE 39-40, NAME 42-71, FSTYEAR 73-76, LSTYEAR 78-81, NOBS 83-88). The WMO index is the last five
  characters of an IGRA id whose characters 4-6 are "000" (e.g. AGM00060390 -> 60390); other ids are not WMO
  stations and are skipped.
- Profiles: University of Wyoming, weather.uwyo.edu/wsgi/sounding?datetime=YYYY-MM-DD HH:MM:SS&id=<WMO>
  &type=TEXT:CSV; columns time, longitude, latitude, pressure_hPa, geopotential height_m, temperature_C,
  dew point temperature_C, ice point temperature_C, relative humidity_% (over water), humidity wrt ice_%,
  mixing ratio_g/kg, wind direction_degree, wind speed_m/s. Only the pressure levels AWCI uses are kept, exactly as
  reported (no vertical interpolation); a level absent from the profile stays absent.
"""

from __future__ import annotations

import csv
import io
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass
from datetime import datetime

from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import PL_LEVELS

UWYO_URL = "https://weather.uwyo.edu/wsgi/sounding"
IGRA_STATIONS_URL = "https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/doc/igra2-station-list.txt"
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"
ATTRIBUTION = "Radiosondages : University of Wyoming ; stations : NOAA NCEI IGRA v2"
_COLUMNS = {"pressure_hPa": "p_hpa", "geopotential height_m": "z_m", "temperature_C": "t_c",
            "dew point temperature_C": "td_c", "relative humidity_%": "rh_pct", "wind direction_degree": "wdir_deg",
            "wind speed_m/s": "wspd_ms"}


class SoundingError(RuntimeError):
    """A sounding could not be obtained or read."""


@dataclass(frozen=True)
class SoundingStation:
    igra_id: str
    wmo: str
    name: str
    lat: float
    lon: float
    elev_m: float | None
    first_year: int
    last_year: int

    def as_dict(self) -> dict[str, object]:
        return {"igra_id": self.igra_id, "wmo": self.wmo, "name": self.name, "lat": self.lat, "lon": self.lon,
                "elev_m": self.elev_m, "first_year": self.first_year, "last_year": self.last_year}


def parse_igra_stations(text: str) -> list[SoundingStation]:
    out = []
    for line in text.splitlines():
        if len(line) < 81:
            continue
        igra_id = line[0:11]
        if igra_id[3:6] != "000":
            continue
        try:
            elev = float(line[31:37])
            out.append(SoundingStation(igra_id=igra_id, wmo=igra_id[6:11], name=line[41:71].strip(),
                                       lat=float(line[12:20]), lon=float(line[21:30]),
                                       elev_m=None if elev <= -998.0 else elev,
                                       first_year=int(line[72:76]), last_year=int(line[77:81])))
        except ValueError:
            continue
    return out


def stations_in(stations: Sequence[SoundingStation], domain: Domain, active_since: int) -> list[SoundingStation]:
    return [s for s in stations if s.last_year >= active_since and domain.contains(s.lat, s.lon)]


def _num(text: str) -> float | None:
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_uwyo_csv(text: str, wmo: str, nominal: datetime,
                   levels: Sequence[int] = PL_LEVELS) -> dict[str, object] | None:
    """One sounding record (AWCI pressure levels only), None when the service returned no profile."""
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows or "pressure_hPa" not in (rows[0] or {}):
        return None
    wanted = {float(p) for p in levels}
    found: dict[float, dict[str, float | None]] = {}
    for row in rows:
        p = _num(row.get("pressure_hPa", ""))
        if p is None or p not in wanted or p in found:
            continue
        found[p] = {name: _num(row.get(col, "")) for col, name in _COLUMNS.items()}
    if not found:
        return None
    first = rows[0]
    lat, lon = _num(first.get("latitude", "")), _num(first.get("longitude", ""))
    return {
        "wmo": wmo, "nominal_time": nominal.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "launch_time": first.get("time", "").strip().replace(" ", "T") + "Z" if first.get("time") else None,
        "lat": lat, "lon": lon,
        "levels": [found[p] | {"p_hpa": p} for p in sorted(found, reverse=True)],
    }


def wind_components(speed_ms: float, direction_deg: float) -> tuple[float, float]:
    """(u, v) from a meteorological wind (direction the wind blows FROM, degrees from north)."""
    d = math.radians(direction_deg)
    return -speed_ms * math.sin(d), -speed_ms * math.cos(d)


class UwyoClient:
    """Sequential client for the Wyoming service (academic: one request at a time, a pause between requests)."""

    def __init__(self, get: Callable[[str], str] | None = None, pause_s: float = 1.0,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self.get = get or self._http_get
        self.pause_s, self.sleep = pause_s, sleep
        self.missing: list[str] = []
        self.errors: list[str] = []

    @staticmethod
    def _http_get(url: str) -> str:
        """The response body; "" when the service answers 404 ("Data Not Found": no sounding at that time)."""
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return str(response.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return ""
            raise SoundingError(f"{url}: {exc}") from exc
        except (OSError, urllib.error.URLError) as exc:
            raise SoundingError(f"{url}: {exc}") from exc

    def sounding(self, wmo: str, nominal: datetime) -> dict[str, object] | None:
        query = urllib.parse.urlencode({"datetime": nominal.strftime("%Y-%m-%d %H:%M:%S"), "id": wmo,
                                        "type": "TEXT:CSV"})
        record = parse_uwyo_csv(self.get(f"{UWYO_URL}?{query}"), wmo, nominal)
        if record is None:
            self.missing.append(f"{wmo}@{nominal:%Y%m%d%H}")
        return record

    def soundings(self, stations: Sequence[SoundingStation], times: Sequence[datetime],
                  skip: Collection[tuple[str, str]] = frozenset()) -> list[dict[str, object]]:
        """Every (station, time) profile available, except the (wmo, "YYYY-MM-DDTHH:MM:SSZ") pairs in `skip`
        (already archived: never requested again). A failed request is recorded in `errors` and skipped;
        SoundingError is raised only when every request failed (service down)."""
        out = []
        pairs = [(s, t) for t in times for s in stations if (s.wmo, f"{t:%Y-%m-%dT%H:%M:%SZ}") not in skip]
        for i, (station, nominal) in enumerate(pairs):
            if i:
                self.sleep(self.pause_s)
            try:
                record = self.sounding(station.wmo, nominal)
            except SoundingError as exc:
                self.errors.append(str(exc))
                continue
            if record is not None:
                out.append(record | {"name": station.name, "elev_m": station.elev_m})
        if pairs and len(self.errors) == len(pairs):
            raise SoundingError(f"all {len(pairs)} requests failed; last: {self.errors[-1]}")
        return out
