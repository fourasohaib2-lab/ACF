"""
Atmospheric Complexity Framework (ACF)

Global Airport & Aeronautical Infrastructure Database Module (ICAO/IATA)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AirportInfo:
    """Description d'un aérodrome international OACI."""
    icao_code: str
    iata_code: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    elevation_ft: float
    runways: List[Dict[str, Any]]
    ils_categories: List[str]
    magnetic_variation_deg: float


AIRPORT_REGISTRY: Dict[str, AirportInfo] = {
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
    ),
}


class AirportDatabase:
    """Base de données et moteur d'infrastructure des aéroports mondiaux."""

    @classmethod
    def get_airport(cls, icao_or_iata: str) -> Optional[AirportInfo]:
        key = icao_or_iata.lower()
        if key in AIRPORT_REGISTRY:
            return AIRPORT_REGISTRY[key]
        for ap in AIRPORT_REGISTRY.values():
            if ap.iata_code.lower() == key:
                return ap
        return None

    @classmethod
    def list_airports(cls) -> List[str]:
        return list(AIRPORT_REGISTRY.keys())
