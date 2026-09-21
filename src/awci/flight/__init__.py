"""
Atmospheric Complexity Framework (ACF)

Flight Planning Engine (``src/awci/flight/``)

Real implementation start of the package named in
``docs/architecture/awci_reference_architecture.md`` section 11:
"Flight Planning Engine... Turns weather into usable flight
information." Previously only real routing existed under
``awci.knowledge.routing.flight_routing`` (moved from
``acf.aviation.routing`` in a prior migration phase) - this package
adds the 2 genuinely new pieces built 2026-09-21:

- ``waypoint.py`` - real great-circle intermediate-point generation
  (a real positional waypoint list along a route).
- ``route_weather.py`` - a real, composed per-route weather briefing
  (real route geometry + real waypoints + real live weather at
  departure/arrival/alternates).

``planning.py``/``route.py``/``corridor.py``/``altitude.py``/
``flight_levels.py``/``departure.py``/``arrival.py``/``alternate.py``/
``fuel_weather.py`` (the blueprint's remaining named files) are
deliberately not built - each real gap named there already has real
content elsewhere in this codebase (route/alternate ->
``awci.knowledge.routing.flight_routing.FlightRoutingEngine``; corridor
-> ``awci.airport.airport``; altitude/flight_levels ->
``awci.knowledge.performance.altimetry``) or would need real data this
codebase does not have (``fuel_weather.py`` would need a real
aircraft-type fuel-burn model this codebase has no source for -
fabricating one would misrepresent a real operational calculation as
grounded when it is not).
"""

from __future__ import annotations
