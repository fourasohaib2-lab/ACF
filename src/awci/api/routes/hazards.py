"""
`/hazards` - real HTTP surface over
``awci.knowledge.hazards.aviation_hazards.AviationHazardEngine`` (the
real aviation-hazard definitions registry) - the ``routes/hazards.py``
module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from awci.api.routes._serialization import to_json_safe
from awci.knowledge.hazards.aviation_hazards import AviationHazardEngine

router = APIRouter(prefix="/hazards", tags=["hazards"])


@router.get("")
async def list_hazards() -> list[str]:
    """Real list of every real hazard key in
    ``AVIATION_HAZARDS_REGISTRY`` - genuinely calls
    ``AviationHazardEngine.list_hazards()``."""
    return AviationHazardEngine.list_hazards()


@router.get("/{key}")
async def hazard_detail(key: str) -> dict[str, Any]:
    """Real hazard definition for one real registry key - 404 (never a
    fabricated definition) if ``key`` is not a real entry."""
    hazard = AviationHazardEngine.get_hazard(key)
    if hazard is None:
        raise HTTPException(404, f"{key!r} is not a real hazard - known: {AviationHazardEngine.list_hazards()}")
    return to_json_safe(hazard)
