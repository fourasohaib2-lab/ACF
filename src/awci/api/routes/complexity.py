"""
`/complexity` - real HTTP surface over
``awci.complexity.calculator.AWCICalculator`` - the ``routes/
complexity.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").

A real, AWCI-native sibling of ``acf.web.routers.complexity_router``
(which serves the same real ``AWCICalculator`` engine, round-tripped
through the ``acf.awci`` backward-compatible shim, at ACF's own
general-purpose FastAPI app) - this one imports ``awci.complexity``
directly rather than via that shim, matching this session's own
"repoint real dependents to the new location directly" discipline
already applied throughout the AWCI package migration.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from awci.complexity.calculator import AWCICalculator

router = APIRouter(prefix="/complexity", tags=["complexity"])


@router.post("/score")
async def score(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Real point complexity score - genuinely calls
    ``AWCICalculator().calculate(data)``, not a canned response. See
    that method's own docstring for ``data``'s real accepted keys
    (temperature, specific_humidity, wind_speed, cape, cin,
    precipitation, pressure, altitude, confidence, temporal_change,
    ensemble_members, model_realizations).
    """
    return AWCICalculator().calculate(data)
