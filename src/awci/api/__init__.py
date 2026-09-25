"""
Atmospheric Complexity Framework (ACF)

AWCI API (``src/awci/api/``)

Real implementation of the package named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API"), previously the specific gap named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("No
dedicated AWCI API surface; ``src/acf/api/`` and ``src/acf/web/`` are
ACF-general, not AWCI-specific"). Real FastAPI (already a declared
optional dependency of this project - see ``pyproject.toml``'s
``web`` extra), following the same real app-assembly pattern already
established by ``acf.web.hpc_dashboard_server.create_app()``.

Built 2026-09-21: ``app.py`` (``create_app()``) plus 6 of the
blueprint's 11 named ``routes/`` modules - the ones with a real,
already-working AWCI backing engine to expose, never a fabricated
endpoint over data this codebase cannot actually produce:

- ``observations.py`` - ``awci.observations.hub.ObservationsHub``
- ``airports.py`` - ``awci.airport.runway``/``awci.airport.weather``
- ``flights.py`` - ``awci.flight.route_weather``
- ``hazards.py`` - ``awci.knowledge.hazards.aviation_hazards``
- ``complexity.py`` - ``awci.complexity.calculator.AWCICalculator``
- ``reports.py`` - ``awci.reports.aviation_report``

Deliberately NOT built this round, and why:

- ``forecasts.py`` - no real AWCI-specific NWP forecast-retrieval
  engine exists to expose; ACF's own ``acf.model4d``/``acf.earth_physics``
  produce forecasts through a genuinely different, heavier pipeline
  (real solver runs, not a per-request HTTP call) with no real
  AWCI-facing adapter built yet.
- ``models.py`` - no real AWCI-specific model-comparison concept
  exists distinct from ``acf.web.routers.models_router``'s own
  already-real, ACF-general model listing - exposing the same real
  data a second time under a different prefix would be duplication,
  not a real gap.
- ``profiles.py`` - ``awci.knowledge.graphics.cross_section.
  FlightCrossSectionEngine`` exists, but (per its own already-
  corrected docstring) only produces real waypoint geometry; every
  atmospheric field it would report (tropopause height, CAT index,
  icing risk) is honestly ``None`` - no real atmospheric data source
  is wired to it. The one real thing it offers (waypoint geometry) is
  already exposed by ``routes/flights.py``'s ``/flights/route-weather``
  - a dedicated endpoint here would add no real value.
- ``maps.py`` - no real AWCI-specific map-tile-serving concept exists
  anywhere in this codebase to expose.
- ``ai.py`` - ``awci.ai`` (the decision-support engine, the RAG layer)
  exists but is a headless Python API, not yet wired to any HTTP
  surface, and several named AI subsystems in the broader remaining-
  gaps list are still unbuilt - a real, disclosed future addition
  once that layer is further along, not fabricated ahead of it.

``schemas/`` is deliberately not a separate subpackage - every
response is a real, already-defined dataclass from its own owning
``awci.*`` module (``RunwayWindAssessment``, ``AirportWeatherSnapshot``,
``RouteWeatherBriefing``, ``AviationReport``, ``AviationHazardInfo``),
converted to a JSON-safe dict by ``routes/_serialization.py`` - adding
a parallel Pydantic schema layer duplicating fields these dataclasses
already declare would be pure repetition with a real drift risk
(two independently-maintained descriptions of the same real data).
``services/`` is also not a separate subpackage - the real service
layer is the already-real ``awci.observations``/``awci.airport``/
``awci.flight``/``awci.knowledge``/``awci.complexity``/``awci.reports``
packages themselves; each route module calls straight into them, the
same direct-call convention ``acf.web.routers`` already uses.
``middleware/`` is not built - no real, specific AWCI middleware need
(auth, rate limiting) exists anywhere in this codebase for any real
API today; nothing here is fabricated ahead of that real need.
"""

from __future__ import annotations
