"""
Atmospheric Complexity Framework (ACF)

Real NEXRAD (WSR-88D) Radar Station Status Connector (NOAA api.weather.gov)

Closes another of the "NOT_CONNECTED" observation feeds disclosed in
acf.gui.esoc.panel_manager.EarthMonitoringPanel (Phase 57) - Doppler
Radar (NEXRAD). Uses api.weather.gov, the real, free, no-authentication
National Weather Service API - its /radar/stations/{id} endpoint
reports each real WSR-88D site's genuine live operational mode, alarm
summary, and Level II data latency (confirmed live during development:
KTLX/KOKX/KJAX all returned real "Operational" status with a real
last-received timestamp within the last minute).

This does not fetch or decode actual reflectivity/velocity volume data
(a much larger undertaking - real Level II/III radar files are binary,
gigabyte-scale per day per site) - only the station's own reported
operational status, which is exactly what an "is this feed alive"
monitoring row needs.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests

#: A handful of real, geographically-spread WSR-88D sites - not
#: exhaustive (NOAA operates ~160 of them), just enough to give an
#: honest "is the NEXRAD network reachable right now" signal without
#: querying all of them on every refresh.
DEFAULT_STATIONS: tuple[str, ...] = ("KTLX", "KOKX", "KJAX")

BASE_URL = "https://api.weather.gov/radar/stations"


@dataclass
class NexradFetchResult:
    """Outcome of one fetch_station_status() call - always honest about
    whether real station status came back, never a fabricated placeholder."""

    is_real_data: bool
    status: str
    stations_operational: int = 0
    stations_total: int = 0
    stations: list[dict[str, Any]] = field(default_factory=list)
    fetched_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict[str, Any]:
        return {
            "is_real_data": self.is_real_data,
            "status": self.status,
            "stations_operational": self.stations_operational,
            "stations_total": self.stations_total,
            "fetched_at": self.fetched_at,
        }


class NEXRADRadarConnector:
    """Real client for NOAA's public api.weather.gov radar station status
    endpoint - no authentication required."""

    def __init__(self, timeout_s: float = 10.0) -> None:
        self.timeout_s = timeout_s

    def fetch_station_status(self, station_ids: tuple[str, ...] = DEFAULT_STATIONS) -> NexradFetchResult:
        """Query each real station in `station_ids` and report how many
        genuinely report an "Operational" RDA mode right now.

        Honest on every failure path: a station that fails to fetch or
        parse is simply not counted as operational (and recorded with
        its own real error in `stations`) - never fabricated as
        reporting, and the aggregate `is_real_data` is only True if at
        least one station was genuinely reached.
        """
        stations: list[dict[str, Any]] = []
        reached_any = False

        for station_id in station_ids:
            try:
                resp = requests.get(
                    f"{BASE_URL}/{station_id}", headers={"Accept": "application/geo+json"}, timeout=self.timeout_s
                )
            except requests.exceptions.RequestException as e:
                stations.append({"id": station_id, "operational": False, "error": f"NETWORK_ERROR: {e}"})
                continue

            if resp.status_code != 200:
                stations.append({"id": station_id, "operational": False, "error": f"HTTP_{resp.status_code}"})
                continue

            try:
                props = resp.json().get("properties", {})
            except ValueError as e:
                stations.append({"id": station_id, "operational": False, "error": f"INVALID_JSON: {e}"})
                continue

            reached_any = True
            mode = (props.get("rda") or {}).get("properties", {}).get("mode")
            stations.append(
                {
                    "id": station_id,
                    "operational": mode == "Operational",
                    "mode": mode,
                    "last_received": (props.get("latency") or {}).get("levelTwoLastReceivedTime"),
                }
            )

        if not reached_any:
            return NexradFetchResult(
                is_real_data=False, status="NOT_FETCHED_NO_STATION_REACHABLE", stations=stations
            )

        operational = sum(1 for s in stations if s.get("operational"))
        return NexradFetchResult(
            is_real_data=True,
            status="FETCHED_OK",
            stations_operational=operational,
            stations_total=len(station_ids),
            stations=stations,
        )
