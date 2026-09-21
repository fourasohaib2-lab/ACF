"""
`/flights` - real HTTP surface over
``awci.flight.route_weather.build_route_weather_briefing`` - the
``routes/flights.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from awci.api.routes._serialization import to_json_safe
from awci.flight.route_weather import build_route_weather_briefing

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/route-weather")
async def route_weather(dep_icao: str, arr_icao: str, request: Request, n_waypoints: int = 10) -> dict[str, Any]:
    """
    Real, composed route weather briefing between two real airports -
    genuinely calls ``build_route_weather_briefing()`` (real route
    geometry, real great-circle waypoints, real live weather at
    departure/arrival/every real recommended alternate), not a canned
    response.
    """
    hub = request.app.state.observations_hub
    try:
        briefing = build_route_weather_briefing(dep_icao, arr_icao, n_waypoints=n_waypoints, hub=hub)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return to_json_safe(briefing)
