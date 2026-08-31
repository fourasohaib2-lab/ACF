"""
Atmospheric Complexity Framework (ACF)

Global Space Weather & Magnetosphere Numerical Models Registry Module (Phase 8)
(WSA-ENLIL, EUHFORIA, BATS-R-US, OpenGGCM, TIE-GCM, IRI, NeQuick, SAMI3)
"""

from dataclasses import dataclass


@dataclass
class SpaceWeatherModelInfo:
    """Description scientifique d'un modèle numérique du Soleil ou de la Magnétosphère."""

    key: str
    name: str
    institution: str
    domain: str  # e.g., "Heliosphere / CME Propagation", "Ionosphere", "Global Magnetosphere"
    governing_equations: str
    typical_lead_time: str
    strengths: list[str]
    references: list[str]


SPACE_WEATHER_MODELS_REGISTRY: dict[str, SpaceWeatherModelInfo] = {
    "wsa_enlil": SpaceWeatherModelInfo(
        key="wsa_enlil",
        name="WSA-ENLIL (Wang-Sheeley-Arge / ENLIL 3D MHD)",
        institution="NOAA SWPC / George Mason University / NASA CCMC",
        domain="Heliosphere / CME Propagation (0.1 to 2.0 AU)",
        governing_equations="3D Time-Dependent Ideal Magnetohydrodynamics (MHD)",
        typical_lead_time="1 à 4 Jours",
        strengths=["Modèle opérationnel de référence à la NOAA pour la vitesse d'impact des CMEs sur Terre"],
        references=["Odstrcil (2003) Adv. Space Res. 32, 497-506"],
    ),
    "batsrus": SpaceWeatherModelInfo(
        key="batsrus",
        name="BATS-R-US (Block-Adaptive Tree Solarwind Roe-Upwind Scheme)",
        institution="University of Michigan Space Environment Modeling Framework (SWMF)",
        domain="Global Magnetosphere & Solar Wind Reconnection",
        governing_equations="Extended 3D MHD avec couplage ionosphérique",
        typical_lead_time="Temps réel / Inférence numérique",
        strengths=["Simulation ultra-précise de la compression magnétosphérique et des indices Dst/Kp"],
        references=["Powell et al. (1999) J. Comput. Phys. 154, 284-309"],
    ),
    "iri": SpaceWeatherModelInfo(
        key="iri",
        name="IRI (International Reference Ionosphere)",
        institution="COSPAR / URSI",
        domain="Global Ionosphere (Electron & Ion Density Profiles 50 to 2000 km)",
        governing_equations="Empirical Ionospheric Model driven by F10.7 & Sunspot Number",
        typical_lead_time="Climatologique / Climatologie ionosphérique",
        strengths=["Standard international (ISO 16457) pour le profil vertical d'électrons et TEC"],
        references=["Bilitza et al. (2017) Radiation Measurements 115, 73-80"],
    ),
}


class SpaceWeatherModelEngine:
    """Moteur de consultation des modèles de temps spatial."""

    @classmethod
    def get_model(cls, key: str) -> SpaceWeatherModelInfo | None:
        return SPACE_WEATHER_MODELS_REGISTRY.get(key.lower())

    @classmethod
    def list_models(cls) -> list[str]:
        return list(SPACE_WEATHER_MODELS_REGISTRY.keys())
