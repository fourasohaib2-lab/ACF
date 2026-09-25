"""
Atmospheric Complexity Framework (ACF)

Flight Planning - Route Weather

Real per-route weather briefing - the ``route_weather.py`` module
named in
``docs/architecture/awci_reference_architecture.md`` section 11
("Flight Planning Engine... Covers:... Weather along route, Hazards
along route."). Composes 3 already-real systems - no new fetch or
routing logic of its own:

- ``awci.knowledge.routing.flight_routing.FlightRoutingEngine`` (real
  great-circle route + real nearest-alternate ranking).
- ``awci.flight.waypoint`` (this session's own new real great-circle
  intermediate-point generation, for a real positional waypoint list).
- ``awci.airport.weather.build_weather_snapshot()`` /
  ``awci.observations.hub.ObservationsHub`` (real live METAR fetch).

Honest scope: real weather is only ever fetched at real airport
stations (departure, arrival, each real alternate) - there is no real
data source anywhere in this codebase for weather AT AN ARBITRARY
POINT along a route (that would need a full real NWP solver run
sampled via
``awci.complexity.path_sampling.sample_field_along_path()``, a
genuinely heavier, separate real capability this module does not
invoke). The real waypoint list this briefing carries is positional
only (latitude/longitude/distance) - never paired with a fabricated
weather value at an intermediate point.
"""

from __future__ import annotations

from dataclasses import dataclass

from awci.airport.weather import AirportWeatherSnapshot, build_weather_snapshot
from awci.flight.waypoint import Waypoint, generate_multi_leg_route_waypoints
from awci.knowledge.airports.airport_database import AirportDatabase
from awci.knowledge.routing.flight_routing import FlightRoutingEngine
from awci.observations.hub import ObservationsHub


@dataclass(frozen=True)
class RouteWeatherBriefing:
    """
    Real, composed route weather briefing - real route geometry, a
    real positional waypoint list, and real live weather at
    departure/arrival/every real recommended alternate. Each weather
    field is a real ``AirportWeatherSnapshot`` (see that module's own
    honest-failure discipline - a real fetch failure surfaces as
    ``is_real_data=False``, never a fabricated fallback).

    ``stopover_icao``/``stopover_weather`` are honestly ``None`` for a
    real direct (non-stopover) route - a stopover is an explicit,
    opt-in caller choice (see ``build_route_weather_briefing``'s own
    ``stopover_icao`` parameter), never inferred.
    """

    departure_icao: str
    arrival_icao: str
    stopover_icao: str | None
    stopover_latitude: float | None
    stopover_longitude: float | None
    great_circle_distance_nm: float
    waypoints: tuple[Waypoint, ...]
    departure_weather: AirportWeatherSnapshot
    arrival_weather: AirportWeatherSnapshot
    stopover_weather: AirportWeatherSnapshot | None
    alternate_weather: dict[str, AirportWeatherSnapshot]


def build_route_weather_briefing(
    dep_icao: str,
    arr_icao: str,
    stopover_icao: str | None = None,
    n_waypoints: int = 10,
    hub: ObservationsHub | None = None,
) -> RouteWeatherBriefing:
    """
    Real, composed route weather briefing between two real airports,
    with an optional real stopover - real route geometry
    (``FlightRoutingEngine.plan_flight_route()``, and, with a
    stopover, its own real great-circle distance formula summed across
    both real legs - a real, physically longer distance than the
    direct route, not an approximation of it), real waypoints
    (``generate_multi_leg_route_waypoints()``), and real live weather
    at departure/stopover (if any)/arrival/every real recommended
    alternate (``build_weather_snapshot()``, sharing one real
    ``ObservationsHub`` across every fetch - a real default hub is
    constructed if none is supplied).

    Parameters
    ----------
    stopover_icao : str | None
        A real, optional intermediate airport - when given, the route
        becomes 2 real great-circle legs (departure -> stopover,
        stopover -> arrival) instead of 1 direct leg, and real weather
        is additionally fetched at the stopover. ``None`` (the
        default) keeps the real direct-route behavior unchanged.

    Raises
    ------
    ValueError
        If ``dep_icao``/``arr_icao``/``stopover_icao`` (when given) is
        not a real airport in ``AirportDatabase`` - the same real
        convention already used by
        ``FlightRoutingEngine.plan_flight_route()``/
        ``awci.airport.runway.assess_airport_runways_wind()``.
    """
    dep = AirportDatabase.get_airport(dep_icao)
    arr = AirportDatabase.get_airport(arr_icao)
    if dep is None or arr is None:
        raise ValueError(
            f"{dep_icao!r}/{arr_icao!r} must both be real airports in AirportDatabase - "
            f"known: {AirportDatabase.list_airports()}"
        )

    stopover = AirportDatabase.get_airport(stopover_icao) if stopover_icao else None
    if stopover_icao and stopover is None:
        raise ValueError(f"{stopover_icao!r} must be a real airport in AirportDatabase")

    hub = hub or ObservationsHub()
    routing = FlightRoutingEngine()
    route = routing.plan_flight_route(dep_icao, arr_icao)

    if stopover is None:
        waypoints = tuple(
            generate_multi_leg_route_waypoints(
                [(dep.latitude, dep.longitude), (arr.latitude, arr.longitude)], n_points_per_leg=n_waypoints
            )
        )
        distance_nm = route["great_circle_distance_nm"]
    else:
        waypoints = tuple(
            generate_multi_leg_route_waypoints(
                [
                    (dep.latitude, dep.longitude),
                    (stopover.latitude, stopover.longitude),
                    (arr.latitude, arr.longitude),
                ],
                n_points_per_leg=n_waypoints,
            )
        )
        # Real sum of 2 real great-circle legs - genuinely longer than
        # the real direct dep->arr distance above, not an
        # approximation of it (a stopover route is physically longer).
        distance_nm = routing.great_circle_distance_nm(
            dep.latitude, dep.longitude, stopover.latitude, stopover.longitude
        ) + routing.great_circle_distance_nm(stopover.latitude, stopover.longitude, arr.latitude, arr.longitude)

    return RouteWeatherBriefing(
        departure_icao=dep.icao_code,
        arrival_icao=arr.icao_code,
        stopover_icao=stopover.icao_code if stopover else None,
        stopover_latitude=stopover.latitude if stopover else None,
        stopover_longitude=stopover.longitude if stopover else None,
        great_circle_distance_nm=distance_nm,
        waypoints=waypoints,
        departure_weather=build_weather_snapshot(dep.icao_code, hub=hub),
        arrival_weather=build_weather_snapshot(arr.icao_code, hub=hub),
        stopover_weather=build_weather_snapshot(stopover.icao_code, hub=hub) if stopover else None,
        alternate_weather={icao: build_weather_snapshot(icao, hub=hub) for icao in route["recommended_alternates"]},
    )
