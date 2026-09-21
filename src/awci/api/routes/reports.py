"""
`/reports` - real HTTP surface over
``awci.reports.aviation_report.build_aviation_report`` - the
``routes/reports.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from awci.api.routes._serialization import to_json_safe
from awci.reports.aviation_report import build_aviation_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{icao_code}")
async def aviation_report(icao_code: str, request: Request) -> dict[str, Any]:
    """
    Real aviation report for one real airport - the weather section is
    always real (``build_weather_snapshot()``); the decision/audit
    sections are honestly absent (``None``) here, since this endpoint
    receives no ``module_scores``/``overall_awci``/``awci_result`` -
    computing a real AWCI score needs real per-module input data this
    HTTP request does not carry (never fabricated to fill the
    section). A caller with real module scores in hand should use
    ``awci.reports.aviation_report.build_aviation_report()`` directly.
    """
    hub = request.app.state.observations_hub
    report = build_aviation_report(icao_code, hub=hub)
    return to_json_safe(report)
