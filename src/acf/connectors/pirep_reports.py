"""
Atmospheric Complexity Framework (ACF)

Real Pilot Report (PIREP) Connector (NOAA aviationweather.gov)

Closes another of the "NOT_CONNECTED" observation feeds disclosed in
acf.gui.esoc.panel_manager.EarthMonitoringPanel (Phase 57) - but
honestly relabeled, not a stand-in for what that row originally said.

Honest scope: this is PIREP (Pilot Report - a pilot's real-time voice/
text report of in-flight conditions: turbulence, icing, cloud tops,
wind), NOT AMDAR (Aircraft Meteorological Data Relay - automated
telemetry from commercial airliners' own sensors, distributed via the
restricted WMO GTS, not a free public feed anywhere ACF could reach).
Confirmed no free public AMDAR feed exists during this investigation -
rather than mislabel PIREP data as "AMDAR" (a different program with a
different data path), the panel row this feeds is renamed to say PIREP
explicitly. Real, free, no-auth NOAA endpoint - confirmed live during
development (real turbulence/icing/cloud reports from real tail
numbers/aircraft types across the continental US).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests

BASE_URL = "https://aviationweather.gov/api/data/pirep"

#: Continental US + approaches - aviationweather.gov's PIREP coverage
#: is overwhelmingly US-sourced (confirmed by inspecting real report
#: `icaoId` values during development), so a global bbox would mostly
#: return nothing extra while costing a much larger response to parse.
DEFAULT_BBOX = "20,-170,75,-50"


@dataclass
class PIREPFetchResult:
    """Outcome of one fetch_recent_reports() call - always honest about
    whether real report data came back, never a fabricated placeholder."""

    is_real_data: bool
    status: str
    report_count: int = 0
    reports: list[dict[str, Any]] = field(default_factory=list)
    fetched_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict[str, Any]:
        return {
            "is_real_data": self.is_real_data,
            "status": self.status,
            "report_count": self.report_count,
            "fetched_at": self.fetched_at,
        }


class PIREPConnector:
    """Real client for NOAA's public aviationweather.gov PIREP endpoint -
    no authentication required."""

    def __init__(self, timeout_s: float = 12.0) -> None:
        self.timeout_s = timeout_s

    def fetch_recent_reports(self, bbox: str = DEFAULT_BBOX) -> PIREPFetchResult:
        """Fetch real, currently-active pilot reports within `bbox`
        ("lat_min,lon_min,lat_max,lon_max").

        Honest on every failure path (network error, non-200 HTTP,
        malformed JSON, unexpected response shape): returns
        is_real_data=False with the real reason in `status`, never a
        fabricated report list - same convention as
        acf.connectors.argo_floats.ArgoFloatsConnector.
        """
        try:
            resp = requests.get(BASE_URL, params={"format": "json", "bbox": bbox}, timeout=self.timeout_s)
        except requests.exceptions.RequestException as e:
            return PIREPFetchResult(is_real_data=False, status=f"NOT_FETCHED_NETWORK_ERROR: {e}")

        if resp.status_code != 200:
            return PIREPFetchResult(
                is_real_data=False, status=f"NOT_FETCHED_HTTP_{resp.status_code}: {resp.text[:200]}"
            )

        try:
            reports = resp.json()
        except ValueError as e:
            return PIREPFetchResult(is_real_data=False, status=f"NOT_FETCHED_INVALID_JSON: {e}")

        if not isinstance(reports, list):
            return PIREPFetchResult(is_real_data=False, status="NOT_FETCHED_UNEXPECTED_RESPONSE_SHAPE")

        return PIREPFetchResult(is_real_data=True, status="FETCHED_OK", report_count=len(reports), reports=reports)
