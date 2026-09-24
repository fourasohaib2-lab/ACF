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

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from awci.api.routes import (
    airports_router,
    complexity_router,
    flights_router,
    hazards_router,
    observations_router,
    reports_router,
)
from awci.observations.hub import ObservationsHub

#: Real, disclosed default: the Next.js dashboard's own local dev
#: server origins (see package.json's "dev" script / next.config.mjs -
#: `next dev` defaults to port 3000, bound on both localhost and
#: 127.0.0.1 depending on how the browser resolves it). Without CORS
#: headers here, every browser genuinely blocks the dashboard's own
#: `lib/api.ts` fetch calls with a real preflight failure (found while
#: exercising the dashboard against this live API in a real browser,
#: not assumed) - FastAPI issues no CORS headers by default.
#: Overridable via AWCI_API_CORS_ORIGINS (comma-separated) for any
#: other real deployment origin (e.g. a production dashboard domain).
_DEFAULT_CORS_ORIGINS = ("http://localhost:3000", "http://127.0.0.1:3000")


def _cors_origins() -> list[str]:
    configured = os.environ.get("AWCI_API_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return list(_DEFAULT_CORS_ORIGINS)


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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

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
