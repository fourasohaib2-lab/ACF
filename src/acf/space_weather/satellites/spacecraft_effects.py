"""
Atmospheric Complexity Framework (ACF)

Satellite Infrastructure Database & Spacecraft Hazards Module (Phase 6)

NOTE (correction — docstring overclaim, found during the post-model4d
audit, 2026-09-05): this header used to name 6 specific satellites/
constellations (GOES, Meteosat, Sentinel, Starlink, GPS, ISS) alongside
2 real hazard phenomena this module does compute (Orbital Drag Decay,
SEUs) as if all 6 satellites were catalogued here too. Only 3 actually
have a SATELLITE_REGISTRY entry: ISS, the Starlink constellation, and
the GPS constellation - GOES, Meteosat, and Sentinel are not
implemented anywhere in this module. Same class of gap as this
session's other registry docstrings - no code behaves incorrectly, only
the header oversold coverage. Corrected to name what SATELLITE_REGISTRY
actually contains.
"""

from dataclasses import dataclass


@dataclass
class SatelliteInfo:
    """Informations de suivi d'un satellite ou constellation orbitale."""

    satellite_id: str
    name: str
    orbit_type: str  # e.g., "LEO", "GEO", "MEO"
    altitude_km: float
    inclination_deg: float
    primary_operator: str
    sensitive_components: list[str]


SATELLITE_REGISTRY: dict[str, SatelliteInfo] = {
    "iss": SatelliteInfo(
        satellite_id="iss",
        name="International Space Station (ISS)",
        orbit_type="LEO",
        altitude_km=420.0,
        inclination_deg=51.6,
        primary_operator="NASA / ESA / Roscosmos / JAXA",
        sensitive_components=["Astronaut EVA Crew", "Solar Arrays", "LEO Atmospheric Drag"],
    ),
    "starlink_constellation": SatelliteInfo(
        satellite_id="starlink_constellation",
        name="Starlink LEO Constellation",
        orbit_type="LEO",
        altitude_km=550.0,
        inclination_deg=53.0,
        primary_operator="SpaceX",
        sensitive_components=["Atmospheric Drag Expansion", "Star Trackers", "K-band Transceivers"],
    ),
    "gps_constellation": SatelliteInfo(
        satellite_id="gps_constellation",
        name="GPS MEO Constellation (NAVSTAR)",
        orbit_type="MEO",
        altitude_km=20200.0,
        inclination_deg=55.0,
        primary_operator="US Space Force",
        sensitive_components=["Atomic Clocks", "Solar Panels", "Outer Van Allen Belt Electrons"],
    ),
}


class SatelliteImpactEngine:
    """Moteur d'évaluation des impacts du temps spatial sur les satellites et engins spatiaux."""

    @staticmethod
    def calculate_leo_drag_increase(f107_index: float, baseline_drag: float = 1.0) -> float:
        """Calcul de l'augmentation du freinage atmosphérique en LEO selon l'indice F10.7."""
        if f107_index <= 70.0:
            return baseline_drag
        return baseline_drag * (1.0 + (f107_index - 70.0) / 50.0)
