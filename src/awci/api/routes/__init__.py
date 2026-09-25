"""
Atmospheric Complexity Framework (ACF)

AWCI API - Routes

Real FastAPI routers, one per real AWCI domain that already has a
real, working backing engine - see ``awci.api``'s own package
docstring for the full list of what is built here versus what is
deliberately not (and why).
"""

from __future__ import annotations

from awci.api.routes.airports import router as airports_router
from awci.api.routes.complexity import router as complexity_router
from awci.api.routes.flights import router as flights_router
from awci.api.routes.hazards import router as hazards_router
from awci.api.routes.observations import router as observations_router
from awci.api.routes.reports import router as reports_router

__all__ = [
    "airports_router",
    "complexity_router",
    "flights_router",
    "hazards_router",
    "observations_router",
    "reports_router",
]
