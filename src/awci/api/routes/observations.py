"""
`/observations` - real HTTP surface over
``awci.observations.hub.ObservationsHub`` - the ``routes/
observations.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from awci.api.routes._serialization import to_json_safe

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get("/{icao_code}")
async def observations_for_station(icao_code: str, request: Request) -> dict[str, Any]:
    """
    Real, single-call aggregation of every real observation source
    for one real station - genuinely calls
    ``ObservationsHub.fetch_all()`` (real METAR/TAF, SIGMET, PIREP,
    NEXRAD status, MTG satellite quicklook), not a canned response.
    Each source honestly reports its own ``is_real_data``/``status``
    on a real fetch failure - never a fabricated fallback.
    """
    hub = request.app.state.observations_hub
    snapshot = hub.fetch_all(icao_code)
    return to_json_safe(snapshot)
