"""
Atmospheric Complexity Framework (ACF)

Real Argo Ocean Float Profile Connector (Argovis public REST API)

Closes one of the 5 "NOT_CONNECTED" observation feeds disclosed in
acf.gui.esoc.panel_manager.EarthMonitoringPanel (Phase 57) - ARGO Ocean
Floats. Uses Argovis (https://argovis.colorado.edu), a real, University
of Colorado-hosted mirror of the international Argo program's real-time
float profile data - public, no API key/authentication required.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import requests


@dataclass
class ArgoFetchResult:
    """Outcome of one fetch_recent_profiles() call - always honest about
    whether real profile data came back, never a fabricated placeholder."""

    is_real_data: bool
    status: str
    profile_count: int = 0
    profiles: list[dict[str, Any]] = field(default_factory=list)
    fetched_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict[str, Any]:
        return {
            "is_real_data": self.is_real_data,
            "status": self.status,
            "profile_count": self.profile_count,
            "fetched_at": self.fetched_at,
        }


class ArgoFloatsConnector:
    """Real client for the public Argovis API (real-time Argo ocean float
    profiles) - see https://argovis.colorado.edu/docs for the underlying
    dataset. No authentication required for the /argo search endpoint used
    here."""

    BASE_URL = "https://argovis-api.colorado.edu"

    def __init__(self, timeout_s: float = 12.0) -> None:
        self.timeout_s = timeout_s

    def fetch_recent_profiles(
        self, hours_back: float = 48.0, bbox: tuple[float, float, float, float] | None = None
    ) -> ArgoFetchResult:
        """Fetch real Argo float profiles reported in the last `hours_back`
        hours, optionally restricted to a (lon_min, lat_min, lon_max,
        lat_max) bounding box - global search if bbox is None.

        Honest on every failure path (network error, non-200 HTTP status,
        malformed/unexpected JSON): returns is_real_data=False with the
        real reason in `status`, never a fabricated profile list - same
        convention as acf.connectors.eumetsat_mtg.EUMETSATMTGConnector.
        """
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=hours_back)
        params: dict[str, Any] = {
            "startDate": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDate": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        if bbox is not None:
            lon_min, lat_min, lon_max, lat_max = bbox
            params["polygon"] = (
                f"[[{lon_min},{lat_min}],[{lon_min},{lat_max}],"
                f"[{lon_max},{lat_max}],[{lon_max},{lat_min}],[{lon_min},{lat_min}]]"
            )

        try:
            resp = requests.get(f"{self.BASE_URL}/argo", params=params, timeout=self.timeout_s)
        except requests.exceptions.RequestException as e:
            return ArgoFetchResult(is_real_data=False, status=f"NOT_FETCHED_NETWORK_ERROR: {e}")

        if resp.status_code != 200:
            return ArgoFetchResult(
                is_real_data=False, status=f"NOT_FETCHED_HTTP_{resp.status_code}: {resp.text[:200]}"
            )

        try:
            profiles = resp.json()
        except ValueError as e:
            return ArgoFetchResult(is_real_data=False, status=f"NOT_FETCHED_INVALID_JSON: {e}")

        if not isinstance(profiles, list):
            return ArgoFetchResult(is_real_data=False, status="NOT_FETCHED_UNEXPECTED_RESPONSE_SHAPE")

        return ArgoFetchResult(
            is_real_data=True, status="FETCHED_OK", profile_count=len(profiles), profiles=profiles
        )
