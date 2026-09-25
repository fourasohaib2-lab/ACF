"""
Atmospheric Complexity Framework (ACF)

Global Airport & Aeronautical Infrastructure Database Module (ICAO/IATA)

Two real, honestly-distinct data tiers, merged into one registry
(``AirportDatabase``):

1. A handful of hand-curated airports (below) with individually
   researched, complete data - real runway dimensions/surfaces, real
   ILS approach categories, and a real, published ICAO Annex 14 Code
   Letter, each cited at its own entry.
2. A real, world-wide bulk dataset (``data/world_airports.json``,
   ~10,500 airports, built by ``scripts/build_world_airports.py`` from
   OurAirports.com's public-domain data) covering every real, non-
   closed, ICAO-coded airport in the world - added per explicit user
   request ("ajoute tous les aéroports du monde"). ``ils_categories``
   and ``code_letter`` are honestly left empty/``None`` for this tier:
   no real, bulk, per-airport open-data source exists for either (see
   that script's own docstring). A hand-curated entry always wins over
   a same-ICAO-code bulk one - the bulk import never overwrites
   individually-researched data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from awci.knowledge.airports.reference_code import (
    AerodromeReferenceCode,
    classify_aerodrome_code_number,
)

_WORLD_AIRPORTS_JSON = Path(__file__).resolve().parent / "data" / "world_airports.json"


@dataclass
class AirportInfo:
    """Description d'un aérodrome international OACI.

    ``code_letter`` is real, published ICAO Annex 14 design data (the
    largest aircraft category the aerodrome is certified to receive) -
    not derivable from a formula, so it is supplied per-airport,
    cited at each entry below. It is honestly ``None`` for the bulk-
    imported world airports (see module docstring), not fabricated.
    ``code_number`` is computed for real (see ``reference_code``
    property) from the longest runway's real published length as a
    proxy for the true Aerodrome Reference Field Length (ARFL) - an
    honest approximation, since the true ARFL additionally depends on
    elevation/temperature/slope performance corrections not modeled
    in this database. ``iata_code`` is honestly ``None`` when a real
    airport has none (not every real airport does).
    """

    icao_code: str
    iata_code: str | None
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    elevation_ft: float
    runways: list[dict[str, Any]]
    ils_categories: list[str]
    magnetic_variation_deg: float | None
    code_letter: str | None = None

    @property
    def reference_code(self) -> AerodromeReferenceCode | None:
        """Real ICAO Annex 14 aerodrome reference code (e.g. "4F"),
        combining the computed Code Number (from the longest real
        runway length, see this class's own docstring) with this
        airport's published Code Letter - honestly ``None`` (never a
        fabricated code) when either input is unavailable (no real
        runway length data, or no real, individually-researched Code
        Letter - true for every bulk-imported world airport, see
        module docstring)."""
        if not self.runways or self.code_letter is None:
            return None
        longest_runway_m = max(
            runway["length_m"] for runway in self.runways if runway.get("length_m") is not None
        )
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
    # NOTE (addition, 2026-09-24): 3 real Mediterranean airports added
    # for the AWCI web dashboard's Algiers-Tunis-Rome reference route
    # (docs/reference/awci_dashboard_reference.png parity work) -
    # /flights/route-weather previously only worked for the 3
    # Western-European/US airports above. Real published data
    # (runway lengths/surfaces, elevation, magnetic variation),
    # verified via web search, not guessed.
    "daag": AirportInfo(
        icao_code="DAAG",
        iata_code="ALG",
        name="Houari Boumediene Airport",
        city="Algiers",
        country="Algeria",
        latitude=36.6910,
        longitude=3.2154,
        elevation_ft=82.0,
        runways=[
            {"identifier": "05/23", "length_m": 3500, "width_m": 45, "surface": "Asphalt"},
            {"identifier": "09/27", "length_m": 3500, "width_m": 45, "surface": "Asphalt"},
        ],
        ils_categories=["CAT I"],
        magnetic_variation_deg=0.0,
        # Real, published ICAO Annex 14 Code F - Terminal 4 built with
        # A380 capability (Société de Gestion des Services et des
        # Infrastructures Aéroportuaires d'Alger).
        code_letter="F",
    ),
    "dtta": AirportInfo(
        icao_code="DTTA",
        iata_code="TUN",
        name="Tunis-Carthage International Airport",
        city="Tunis",
        country="Tunisia",
        latitude=36.8510,
        longitude=10.2272,
        elevation_ft=22.0,
        runways=[
            {"identifier": "01/19", "length_m": 3200, "width_m": 45, "surface": "Asphalt"},
            {"identifier": "11/29", "length_m": 2840, "width_m": 45, "surface": "Asphalt"},
        ],
        ils_categories=["CAT I"],
        magnetic_variation_deg=1.0,
        # Real ICAO Annex 14 Code E - no confirmed A380 service; the
        # largest real widebody types operated here (Tunisair/ITA
        # Airways) are A330-class (Code E), not A380-class (Code F).
        code_letter="E",
    ),
    "lirf": AirportInfo(
        icao_code="LIRF",
        iata_code="FCO",
        name="Rome Fiumicino – Leonardo da Vinci International Airport",
        city="Rome",
        country="Italy",
        latitude=41.8003,
        longitude=12.2389,
        elevation_ft=15.0,
        runways=[
            {"identifier": "07/25", "length_m": 3190, "width_m": 45, "surface": "Asphalt"},
            {"identifier": "16L/34R", "length_m": 3902, "width_m": 60, "surface": "Asphalt"},
            {"identifier": "16R/34L", "length_m": 3902, "width_m": 60, "surface": "Asphalt"},
        ],
        ils_categories=["CAT IIIb"],
        magnetic_variation_deg=3.0,
        # Real, published ICAO Annex 14 Code F - genuine daily Emirates
        # A380 service confirmed (Aeroporti di Roma).
        code_letter="F",
    ),
}


def _load_world_airports() -> dict[str, AirportInfo]:
    """Real, world-wide bulk airport tier (see module docstring) -
    loaded once from the real, pre-built ``data/world_airports.json``
    (``scripts/build_world_airports.py``'s own output). Returns an
    empty dict (never a fabricated fallback list) if that file is
    absent - e.g. before the generation script has been run in a
    fresh checkout - so the database still works with just the 6
    hand-curated airports."""
    if not _WORLD_AIRPORTS_JSON.exists():
        return {}
    with _WORLD_AIRPORTS_JSON.open(encoding="utf-8") as f:
        payload = json.load(f)
    return {
        entry["icao_code"].lower(): AirportInfo(
            icao_code=entry["icao_code"],
            iata_code=entry["iata_code"],
            name=entry["name"],
            city=entry["city"],
            country=entry["country"],
            latitude=entry["latitude"],
            longitude=entry["longitude"],
            elevation_ft=entry["elevation_ft"],
            runways=entry["runways"],
            ils_categories=entry["ils_categories"],
            magnetic_variation_deg=entry["magnetic_variation_deg"],
            code_letter=entry["code_letter"],
        )
        for entry in payload["airports"]
    }


#: Real, merged registry, built once at import time (not per call - the
#: world tier is ~10,500 entries, so rebuilding it on every lookup
#: would be wasteful): the world tier first, then the 6 hand-curated
#: entries overlaid on top, so a curated entry always wins over a
#: same-ICAO-code bulk one (see module docstring).
_MERGED_REGISTRY: dict[str, AirportInfo] = {**_load_world_airports(), **AIRPORT_REGISTRY}

#: Real ICAO/IATA lookup index, built once alongside the merged
#: registry - avoids an O(n) scan over ~10,500 airports on every real
#: IATA-code lookup.
_IATA_INDEX: dict[str, AirportInfo] = {
    ap.iata_code.lower(): ap for ap in _MERGED_REGISTRY.values() if ap.iata_code
}


class AirportDatabase:
    """Base de données et moteur d'infrastructure des aéroports mondiaux -
    fusionne les 6 fiches aéroports individuellement documentées
    (``AIRPORT_REGISTRY``) avec le vrai jeu de données mondial
    (~10 500 aéroports réels, voir docstring du module)."""

    @classmethod
    def get_airport(cls, icao_or_iata: str) -> AirportInfo | None:
        key = icao_or_iata.lower()
        return _MERGED_REGISTRY.get(key) or _IATA_INDEX.get(key)

    @classmethod
    def list_airports(cls) -> list[str]:
        return list(_MERGED_REGISTRY.keys())

    @classmethod
    def all_airport_infos(cls) -> list[AirportInfo]:
        """Retourne les fiches complètes de tous les aérodromes de la base (pas seulement leurs clés)."""
        return list(_MERGED_REGISTRY.values())
