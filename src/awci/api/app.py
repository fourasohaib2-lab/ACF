"""
Atmospheric Complexity Framework (ACF)

AWCI API - Application

Real ``create_app()`` - the ``app.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API"). Follows the same real FastAPI-assembly pattern already
established by ``acf.web.hpc_dashboard_server.create_app()``
(construct ``FastAPI``, stash injectable real dependencies on
``app.state`` for tests, ``include_router()`` every real domain
router) - a genuinely new, separate app for AWCI's own real domain
routers, not added to ACF's existing general-purpose web app (matching
the reference architecture's own framing of AWCI as a separate
product).
"""

from __future__ import annotations

from fastapi import FastAPI

from awci.api.routes import (
    airports_router,
    complexity_router,
    flights_router,
    hazards_router,
    observations_router,
    reports_router,
)
from awci.observations.hub import ObservationsHub


def create_app(observations_hub: ObservationsHub | None = None) -> FastAPI:
    """
    Build the AWCI FastAPI app.

    Parameters
    ----------
    observations_hub : ObservationsHub, optional
        Injected for tests (a real, pre-configured or monkeypatched
        hub, avoiding real network calls in test runs - the same real
        injection convention ``acf.web.hpc_dashboard_server.
        create_app()`` already established for its own ``hpc``/
        ``neural_engine`` parameters). Defaults to a real, freshly
        constructed ``ObservationsHub`` for actual application use.
    """
    app = FastAPI(title="AWCI API", description="Aviation Weather Complexity Index - real aviation data API")
    app.state.observations_hub = observations_hub or ObservationsHub()

    app.include_router(observations_router)
    app.include_router(airports_router)
    app.include_router(flights_router)
    app.include_router(hazards_router)
    app.include_router(complexity_router)
    app.include_router(reports_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "awci-api"}

    return app
