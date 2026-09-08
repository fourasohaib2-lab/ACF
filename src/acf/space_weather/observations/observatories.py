"""
Atmospheric Complexity Framework (ACF)

Heliophysics Observatories & Spacecraft Observatory Registry Module (Phase 9)

NOTE (correction — docstring overclaim, found during the post-model4d
audit, 2026-09-05): this header used to name 8 observatories (SDO,
SOHO, ACE, DSCOVR, STEREO, Parker Solar Probe, Solar Orbiter, GOES) as
if all were catalogued here. Only 2 actually have a
SPACE_OBSERVATORIES_REGISTRY entry: DSCOVR and SDO - the other 6
(SOHO, ACE, STEREO, Parker Solar Probe, Solar Orbiter, GOES) are not
implemented anywhere in this module. Same class of gap as this
session's other registry docstrings (acf.climate, acf.ocean,
acf.planetary, this package's own models/space_models.py) - no code
behaves incorrectly (SpaceObservatoryEngine.get_observatory() honestly
returns None for any of the 6 missing keys), only the header oversold
coverage. Corrected to name what SPACE_OBSERVATORIES_REGISTRY actually
contains.
"""

from dataclasses import dataclass


@dataclass
class SpaceObservatoryInfo:
    """Description d'un observatoire spatial ou satellite de physique solaire."""

    key: str
    name: str
    agency: str
    orbit_location: str  # e.g., "Sun-Earth L1 Lagrange Point", "Geostationary GEO", "Heliocentric"
    primary_instruments: list[str]
    scientific_payload: str
    references: list[str]


SPACE_OBSERVATORIES_REGISTRY: dict[str, SpaceObservatoryInfo] = {
    "dscovr": SpaceObservatoryInfo(
        key="dscovr",
        name="DSCOVR (Deep Space Climate Observatory)",
        agency="NOAA / NASA / US Air Force",
        orbit_location="Point de Lagrange L1 (1.5 million km de la Terre)",
        primary_instruments=["PlasMag (Faraday Cup & Magnetometer)", "EPAM"],
        scientific_payload="Mesure du vent solaire en direct ~45 min avant l'impact sur Terre (Vsw, B_z)",
        references=["NOAA SWPC DSCOVR Mission Overview"],
    ),
    "sdo": SpaceObservatoryInfo(
        key="sdo",
        name="SDO (Solar Dynamics Observatory)",
        agency="NASA",
        orbit_location="Orbite Géosynchrone (GEO)",
        primary_instruments=["AIA (Atmospheric Imaging Assembly)", "HMI", "EVE"],
        scientific_payload="Imagerie EUV du Soleil haute résolution (1024x1024) et magnétogrammes HMI",
        references=["Pesnell et al. (2012) Solar Physics 275, 3-15"],
    ),
}


class SpaceObservatoryEngine:
    """Moteur de consultation des observatoires spatiaux et satellites de mesure L1."""

    @classmethod
    def get_observatory(cls, key: str) -> SpaceObservatoryInfo | None:
        return SPACE_OBSERVATORIES_REGISTRY.get(key.lower())

    @classmethod
    def list_observatories(cls) -> list[str]:
        return list(SPACE_OBSERVATORIES_REGISTRY.keys())
