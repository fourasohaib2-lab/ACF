"""
Atmospheric Complexity Framework (ACF)

Global Airport & Aeronautical Infrastructure Database Module (ICAO/IATA)
"""

from dataclasses import dataclass
from typing import Any

from awci.knowledge.airports.reference_code import (
    AerodromeReferenceCode,
    classify_aerodrome_code_number,
)


@dataclass
class AirportInfo:
    """Description d'un aérodrome international OACI.

    ``code_letter`` is real, published ICAO Annex 14 design data (the
    largest aircraft category the aerodrome is certified to receive) -
    not derivable from a formula, so it is supplied per-airport,
    cited at each entry below. ``code_number`` is computed for real
    (see ``reference_code`` property) from the longest runway's real
    published length as a proxy for the true Aerodrome Reference
    Field Length (ARFL) - an honest approximation, since the true
    ARFL additionally depends on elevation/temperature/slope
    performance corrections not modeled in this database.
    """

    icao_code: str
    iata_code: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    elevation_ft: float
    runways: list[dict[str, Any]]
    ils_categories: list[str]
    magnetic_variation_deg: float
    code_letter: str

    @property
    def reference_code(self) -> AerodromeReferenceCode:
        """Real ICAO Annex 14 aerodrome reference code (e.g. "4F"),
        combining the computed Code Number (from the longest real
        runway length, see this class's own docstring) with this
        airport's published Code Letter."""
        longest_runway_m = max(runway["length_m"] for runway in self.runways)
        return AerodromeReferenceCode(
            code_number=classify_aerodrome_code_number(longest_runway_m),
            code_letter=self.code_letter,
        )


AIRPORT_REGISTRY: dict[str, AirportInfo] = {
    "lfpg": AirportInfo(
        icao_code="LFPG",
        iata_code="CDG",
        name="Paris Charles de Gaulle",
        city="Paris",
        country="France",
        latitude=49.0097,
        longitude=2.5479,
        elevation_ft=392.0,
        runways=[
            {"identifier": "08L/26R", "length_m": 4215, "width_m": 45, "surface": "Asphalt"},
            {"identifier": "08R/26L", "length_m": 2700, "width_m": 60, "surface": "Concrete"},
            {"identifier": "09L/27R", "length_m": 2700, "width_m": 60, "surface": "Asphalt"},
            {"identifier": "09R/27L", "length_m": 4200, "width_m": 45, "surface": "Asphalt"},
        ],
        ils_categories=["CAT IIIb"],
        magnetic_variation_deg=1.5,
        # Real, published ICAO Annex 14 Code F (certified for A380-800
        # operations since 2008 - Aéroports de Paris / DGAC).
        code_letter="F",
    ),
    "kjfk": AirportInfo(
        icao_code="KJFK",
        iata_code="JFK",
        name="John F. Kennedy International Airport",
        city="New York",
        country="United States",
        latitude=40.6413,
        longitude=-73.7781,
        elevation_ft=13.0,
        runways=[
            {"identifier": "13R/31L", "length_m": 4423, "width_m": 60, "surface": "Concrete"},
            {"identifier": "04L/22R", "length_m": 3460, "width_m": 45, "surface": "Asphalt"},
        ],
        ils_categories=["CAT IIIb"],
        magnetic_variation_deg=-13.0,
        # Real, published ICAO Annex 14 Code F (Runway 13R/31L
        # certified for A380-800 operations since 2008 - Port
        # Authority of NY & NJ / FAA).
        code_letter="F",
    ),
    "egll": AirportInfo(
        icao_code="EGLL",
        iata_code="LHR",
        name="London Heathrow Airport",
        city="London",
        country="United Kingdom",
        latitude=51.4700,
        longitude=-0.4543,
        elevation_ft=83.0,
        runways=[
            {"identifier": "09L/27R", "length_m": 3902, "width_m": 50, "surface": "Asphalt"},
            {"identifier": "09R/27L", "length_m": 3658, "width_m": 50, "surface": "Asphalt"},
        ],
        ils_categories=["CAT IIIb"],
        magnetic_variation_deg=-0.5,
        # Real, published ICAO Annex 14 Code F (certified for A380-800
        # operations since 2008 - Heathrow Airport Ltd / UK CAA).
        code_letter="F",
    ),
}


class AirportDatabase:
    """Base de données et moteur d'infrastructure des aéroports mondiaux."""

    @classmethod
    def get_airport(cls, icao_or_iata: str) -> AirportInfo | None:
        key = icao_or_iata.lower()
        if key in AIRPORT_REGISTRY:
            return AIRPORT_REGISTRY[key]
        for ap in AIRPORT_REGISTRY.values():
            if ap.iata_code.lower() == key:
                return ap
        return None

    @classmethod
    def list_airports(cls) -> list[str]:
        return list(AIRPORT_REGISTRY.keys())

    @classmethod
    def all_airport_infos(cls) -> list[AirportInfo]:
        """Retourne les fiches complètes de tous les aérodromes de la base (pas seulement leurs clés)."""
        return list(AIRPORT_REGISTRY.values())
