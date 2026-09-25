"""AWCI aviation knowledge base.

Migrated 2026-09-21 (Phase 9 of the AWCI separate-package migration -
see ``awci``'s own package docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``) from
``acf.aviation`` - the whole package moved as one coherent unit
(airports/, graphics/, hazards/, icao/, performance/, routing/),
preserving its own internal structure. This is the blueprint's own
``awci/knowledge/`` "Aviation Knowledge Base" layer: real airport data,
aircraft performance, real METAR/TAF/SIGMET decoders and live source,
flight routing, and the aviation hazard definitions registry used by
``awci.hazards``'s own per-point computations (a distinct, narrower
concept from this package's own ``hazards/aviation_hazards.py``
registry - see the gap analysis for the disclosed distinction).
``acf.aviation.<x>`` is kept as a real backward-compatible re-export
for every module.
"""

from awci.knowledge.airports.airport_database import AirportDatabase, AirportInfo
from awci.knowledge.graphics.cross_section import FlightCrossSectionEngine
from awci.knowledge.hazards.aviation_hazards import AviationHazardEngine, AviationHazardInfo
from awci.knowledge.icao.products import ICAOMetDecoder, METARData, SIGMETData, TAFData
from awci.knowledge.performance.aircraft_performance import AircraftPerformanceEngine
from awci.knowledge.routing.flight_routing import FlightRoutingEngine

__all__ = [
    "AircraftPerformanceEngine",
    "AirportDatabase",
    "AirportInfo",
    "AviationHazardEngine",
    "AviationHazardInfo",
    "FlightCrossSectionEngine",
    "FlightRoutingEngine",
    "ICAOMetDecoder",
    "METARData",
    "SIGMETData",
    "TAFData",
]
