"""
`/api/v1/events` - real HTTP surface over the Event Engine
(`acf.events` - real detectors + `Event`'s own enforced lifecycle).

Storage note: detected events are kept in a real, plain in-memory
dict on `request.app.state.event_store` - not a database. A restart
loses them. This is a deliberate, disclosed choice for this phase, not
an oversight: no Event persistence layer exists anywhere in ACF yet
(building one is separate, larger work), and an in-memory store is
still enough to genuinely exercise the real lifecycle
(`Event.transition_to()`) over HTTP across multiple requests, which is
the real thing this router needs to prove works, not where events are
stored long-term.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from acf.events.detectors.fog_detector import DEFAULT_RH_THRESHOLD_PCT, detect_fog_favorable_events
from acf.events.detectors.wind_detector import DEFAULT_THRESHOLD_M_S as DEFAULT_WIND_SPEED_THRESHOLD_M_S
from acf.events.detectors.wind_detector import detect_strong_wind_events
from acf.events.event import Event, IllegalEventTransitionError
from acf.web.routers._solver_guard import run_complexity_field

router = APIRouter(prefix="/events", tags=["events"])

#: The only two event types with a real, defensible detector today -
#: see acf.events package docstring for exactly why the other 6 named
#: in the Prompt Maître (Thunderstorm, Cyclone, HeavyRain, Hail, Snow,
#: Dust) have none: they need real data (CAPE, precipitation, aerosol
#: concentration...) that does not exist anywhere in ACF's real solver
#: output.
_DETECTORS = ("strong_wind", "fog_favorable_conditions")


def _get_store(request: Request) -> dict[str, Event]:
    store = getattr(request.app.state, "event_store", None)
    if store is None:
        store = {}
        request.app.state.event_store = store
    return store


@router.post("/detect")
async def detect(
    request: Request,
    model: str = "ARPEGE",
    event_type: str = "strong_wind",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    seed: int = 0,
    threshold: float | None = None,
) -> list[dict[str, Any]]:
    """
    Genuinely run `CoupledEarthSolver` (via `compute_real_complexity_field()`,
    same request-size guard as `/api/v1/complexity/field`), then the
    real detector for `event_type` on that real field. Every returned
    `Event` is also stored (`event_id` keyed) so its real lifecycle can
    be advanced via `POST /{event_id}/transition` afterwards.
    """
    if event_type not in _DETECTORS:
        raise HTTPException(
            400,
            f"Unknown or unsupported event_type {event_type!r} - only {_DETECTORS} have a real detector "
            f"today (see acf.events package docstring for why the others are honestly not built)",
        )
    result = run_complexity_field(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, seed=seed)

    events: list[Event]
    if event_type == "strong_wind":
        events = detect_strong_wind_events(
            result["wind_speed_field"],
            result["lats"],
            result["lons"],
            model=model,
            threshold_m_s=threshold if threshold is not None else DEFAULT_WIND_SPEED_THRESHOLD_M_S,
        )
    else:
        events = detect_fog_favorable_events(
            result["temperature_field"],
            result["specific_humidity_field"],
            result["pressure_field_hpa"],
            result["wind_speed_field"],
            result["lats"],
            result["lons"],
            model=model,
            rh_threshold_pct=threshold if threshold is not None else DEFAULT_RH_THRESHOLD_PCT,
        )

    store = _get_store(request)
    for e in events:
        store[e.event_id] = e
    return [jsonable_encoder(e) for e in events]


@router.get("")
async def list_events(request: Request) -> list[dict[str, Any]]:
    """Every event detected via this server process since it started (see this module's own storage note)."""
    return [jsonable_encoder(e) for e in _get_store(request).values()]


@router.get("/{event_id}")
async def get_event(event_id: str, request: Request) -> dict[str, Any]:
    store = _get_store(request)
    if event_id not in store:
        raise HTTPException(404, f"No event {event_id!r} in this server's event store")
    return jsonable_encoder(store[event_id])


@router.post("/{event_id}/transition")
async def transition_event(event_id: str, request: Request, new_status: str = Body(..., embed=True)) -> dict[str, Any]:
    """
    Genuinely call `Event.transition_to(new_status)` - a real, enforced
    state machine (`acf.events.event._LEGAL_TRANSITIONS`), not a status
    field a caller can set to anything. An illegal transition is
    reported as HTTP 409, not silently accepted or a generic 500.
    """
    store = _get_store(request)
    if event_id not in store:
        raise HTTPException(404, f"No event {event_id!r} in this server's event store")
    event = store[event_id]
    try:
        event.transition_to(new_status)
    except IllegalEventTransitionError as exc:
        raise HTTPException(409, str(exc)) from exc
    return jsonable_encoder(event)
