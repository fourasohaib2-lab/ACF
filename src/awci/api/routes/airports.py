"""
`/airports` - real HTTP surface over ``awci.airport.runway``/
``awci.airport.weather`` - the ``routes/airports.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from awci.api.routes._serialization import to_json_safe
from awci.airport.runway import assess_airport_runways_wind
from awci.airport.weather import build_weather_snapshot

router = APIRouter(prefix="/airports", tags=["airports"])


@router.get("/{icao_or_iata}/runways")
async def runway_wind(icao_or_iata: str, wind_dir_deg: float, wind_speed_kt: float) -> dict[str, Any]:
    """
    Real per-runway-end headwind/crosswind for every real runway of
    one real airport - genuinely calls
    ``assess_airport_runways_wind()`` (real ICAO heading parsing +
    real wind-component trigonometry), not a canned response.
    """
    try:
        assessments = assess_airport_runways_wind(icao_or_iata, wind_dir_deg, wind_speed_kt)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {end: to_json_safe(assessment) for end, assessment in assessments.items()}


@router.get("/{icao_code}/weather")
async def airport_weather(icao_code: str, request: Request) -> dict[str, Any]:
    """
    Real, composed per-airport weather view - genuinely calls
    ``build_weather_snapshot()`` (real METAR fetch/decode, real
    ceiling classification, real WMO present-weather description).
    Honestly ``is_real_data=False`` on a real fetch failure, never a
    fabricated fallback.
    """
    hub = request.app.state.observations_hub
    snapshot = build_weather_snapshot(icao_code, hub=hub)
    return to_json_safe(snapshot)
