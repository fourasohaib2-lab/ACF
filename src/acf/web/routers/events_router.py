"""
`/api/v1/events` - real HTTP surface over the Event Engine
(`acf.events` - real detectors + `Event`'s own enforced lifecycle).

Storage: a real, durable `acf.web.storage.SqliteDocumentStore` on
`request.app.state.event_store` - closes reports/ACF_MASTER_AUDIT_v2.md's
own "/api/v1/events remain in-memory (real, disclosed, not durable)"
follow-up. `Event.to_dict()`/`from_dict()` (on the contract itself,
reused here rather than duplicated) give an exact round trip - an
event's real lifecycle `status` (and everything else about it) is
still there, correctly, after a server restart.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from acf.events.detectors.fog_detector import DEFAULT_RH_THRESHOLD_PCT, detect_fog_favorable_events
from acf.events.detectors.wind_detector import DEFAULT_THRESHOLD_M_S as DEFAULT_WIND_SPEED_THRESHOLD_M_S
from acf.events.detectors.wind_detector import detect_strong_wind_events
from acf.events.event import Event, IllegalEventTransitionError
from acf.web.routers._solver_guard import run_complexity_field
from acf.web.storage import SqliteDocumentStore

router = APIRouter(prefix="/events", tags=["events"])

#: Real default location for the durable store - see
#: acf.web.routers.datasets_router.DEFAULT_DATASET_DB_PATH's own note
#: on why this is anchored under <repo_root>/data/.
DEFAULT_EVENT_DB_PATH = Path(__file__).resolve().parents[4] / "data" / "web" / "events.db"

#: The only two event types with a real, defensible detector today -
#: see acf.events package docstring for exactly why the other 6 named
#: in the Prompt Maître (Thunderstorm, Cyclone, HeavyRain, Hail, Snow,
#: Dust) have none: they need real data (CAPE, precipitation, aerosol
#: concentration...) that does not exist anywhere in ACF's real solver
#: output.
_DETECTORS = ("strong_wind", "fog_favorable_conditions")


def _get_store(request: Request) -> SqliteDocumentStore:
    store = getattr(request.app.state, "event_store", None)
    if store is None:
        path = getattr(request.app.state, "event_db_path", None) or DEFAULT_EVENT_DB_PATH
        store = SqliteDocumentStore(path)
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
    `Event` is also durably stored (`event_id` keyed) so its real
    lifecycle can be advanced via `POST /{event_id}/transition`
    afterwards, including after a server restart.
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
        store.set(e.event_id, e.to_dict())
    return [jsonable_encoder(e) for e in events]


@router.get("")
async def list_events(request: Request) -> list[dict[str, Any]]:
    """Every event ever detected via this server's durable store (see this module's own storage note) - survives a restart."""
    return [jsonable_encoder(Event.from_dict(d)) for d in _get_store(request).list()]


@router.get("/{event_id}")
async def get_event(event_id: str, request: Request) -> dict[str, Any]:
    stored = _get_store(request).get(event_id)
    if stored is None:
        raise HTTPException(404, f"No event {event_id!r} in this server's event store")
    return jsonable_encoder(Event.from_dict(stored))


@router.post("/{event_id}/transition")
async def transition_event(event_id: str, request: Request, new_status: str = Body(..., embed=True)) -> dict[str, Any]:
    """
    Genuinely call `Event.transition_to(new_status)` - a real, enforced
    state machine (`acf.events.event._LEGAL_TRANSITIONS`), not a status
    field a caller can set to anything. An illegal transition is
    reported as HTTP 409, not silently accepted or a generic 500. The
    real resulting status is durably persisted back to the store.
    """
    store = _get_store(request)
    stored = store.get(event_id)
    if stored is None:
        raise HTTPException(404, f"No event {event_id!r} in this server's event store")
    event = Event.from_dict(stored)
    try:
        event.transition_to(new_status)
    except IllegalEventTransitionError as exc:
        raise HTTPException(409, str(exc)) from exc
    store.set(event.event_id, event.to_dict())
    return jsonable_encoder(event)
