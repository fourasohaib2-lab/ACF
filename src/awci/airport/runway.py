"""
Atmospheric Complexity Framework (ACF)

Airport Operations - Runway Wind Assessment

Real per-runway-end headwind/crosswind assessment - the ``runway.py``
module named in
``docs/architecture/awci_reference_architecture.md`` section 12
("Airport Operations... Chain: Weather → Airport → Runway →
Operation"). No new physics: composes 2 already-real pieces -
``awci.airport.airport.parse_runway_heading_magnetic_deg()`` (real
ICAO runway-identifier → magnetic-heading convention) and
``awci.knowledge.performance.aircraft_performance.
AircraftPerformanceEngine.wind_components()`` (real headwind/crosswind
trigonometry) - neither reimplemented here.
"""

from __future__ import annotations

from dataclasses import dataclass

from awci.airport.airport import parse_runway_heading_magnetic_deg
from awci.knowledge.airports.airport_database import AirportDatabase
from awci.knowledge.performance.aircraft_performance import AircraftPerformanceEngine


@dataclass(frozen=True)
class RunwayWindAssessment:
    """Real headwind/crosswind assessment for one real runway end,
    given a real wind direction/speed."""

    runway_end_identifier: str
    runway_heading_magnetic_deg: float
    headwind_kt: float
    crosswind_kt: float
    crosswind_direction: str


def assess_runway_end_wind(
    runway_end_identifier: str, wind_dir_deg: float, wind_speed_kt: float
) -> RunwayWindAssessment:
    """
    Real headwind/crosswind assessment for one real runway end - the
    real heading is parsed from ``runway_end_identifier`` (e.g. "08L"),
    and the real wind components are computed for it. Computes nothing
    new: a thin, real composition of the 2 already-real functions named
    in this module's own docstring.
    """
    heading = parse_runway_heading_magnetic_deg(runway_end_identifier)
    components = AircraftPerformanceEngine.wind_components(heading, wind_dir_deg, wind_speed_kt)
    return RunwayWindAssessment(
        runway_end_identifier=runway_end_identifier,
        runway_heading_magnetic_deg=heading,
        headwind_kt=components["headwind_kt"],
        crosswind_kt=components["crosswind_kt"],
        crosswind_direction=components["crosswind_direction"],
    )


def assess_airport_runways_wind(
    icao_or_iata: str, wind_dir_deg: float, wind_speed_kt: float
) -> dict[str, RunwayWindAssessment]:
    """
    Real per-runway-end wind assessment for every real runway of one
    real airport - a convenience wrapper over
    ``assess_runway_end_wind()``, iterating
    ``AirportDatabase.get_airport()``'s own real ``runways`` list (the
    same real iteration convention already used by
    ``awci.airport.airport.compute_airport_corridors()``).

    Raises
    ------
    ValueError
        If ``icao_or_iata`` is not a real airport in
        ``AirportDatabase`` (never a fabricated/guessed airport).
    """
    airport = AirportDatabase.get_airport(icao_or_iata)
    if airport is None:
        raise ValueError(
            f"{icao_or_iata!r} is not a real airport in AirportDatabase - known: {AirportDatabase.list_airports()}"
        )
    assessments: dict[str, RunwayWindAssessment] = {}
    for runway in airport.runways:
        for end_identifier in runway["identifier"].split("/"):
            assessments[end_identifier] = assess_runway_end_wind(end_identifier, wind_dir_deg, wind_speed_kt)
    return assessments


def best_runway_end_for_wind(icao_or_iata: str, wind_dir_deg: float, wind_speed_kt: float) -> RunwayWindAssessment:
    """
    Real selection of the runway end with the real HIGHEST headwind
    among a real airport's runway ends - matches real operational
    practice (landing/taking off into the wind minimizes both
    crosswind and ground-roll distance for the same real wind vector,
    since reciprocal runway ends always have exactly opposite real
    headwind/crosswind signs). A real comparison of already-computed
    real values, not a new formula.
    """
    assessments = assess_airport_runways_wind(icao_or_iata, wind_dir_deg, wind_speed_kt)
    return max(assessments.values(), key=lambda assessment: assessment.headwind_kt)
