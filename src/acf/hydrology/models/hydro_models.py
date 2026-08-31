"""
Atmospheric Complexity Framework (ACF)

Global Hydrological Numerical Models Registry Module (Phase 3)
(HEC-HMS, HEC-RAS, LISFLOOD, VIC, SWAT, MIKE SHE, WRF-Hydro, CaMa-Flood)
"""

from dataclasses import dataclass


@dataclass
class HydrologicalModelInfo:
    """Description scientifique d'un modèle numérique hydrologique / hydraulique."""

    key: str
    name: str
    institution: str
    physics_type: str  # e.g., "Distributed Hydrological & Channel Routing Engine"
    governing_equations: str
    typical_resolution: str
    strengths: list[str]
    limitations: list[str]
    references: list[str]


HYDROLOGICAL_MODELS_REGISTRY: dict[str, HydrologicalModelInfo] = {
    "lisflood": HydrologicalModelInfo(
        key="lisflood",
        name="LISFLOOD (ECMWF / Copernicus EFAS & GloFAS)",
        institution="ECMWF / European Commission Joint Research Centre (JRC)",
        governing_equations="Grid-based Distributed Hydrological & Kinematic Wave Channel Routing",
        physics_type="Couplage Bilan d'Eau 2L + Routage Kinématique en Rivière",
        typical_resolution="5 km Global / 1 km Européen (EFAS)",
        strengths=["Modèle de référence de l'EFAS et du GloFAS pour les alertes aux inondations majeures"],
        limitations=["Sensible au calage des paramètres de rugosité Manning n en chenal"],
        references=["Van Der Knijff et al. (2010) JRC Scientific and Technical Reports", "Burek et al. (2013)"],
    ),
    "hec_hms": HydrologicalModelInfo(
        key="hec_hms",
        name="HEC-HMS (Hydrologic Engineering Center's Hydrologic Modeling System)",
        institution="US Army Corps of Engineers (USACE)",
        governing_equations="SCS Runoff / Green-Ampt + Hydrogramme Unitaire & Muskingum / Kinematic Wave",
        physics_type="Lumped & Semi-Distributed Watershed Modeling System",
        typical_resolution="Échelle du Bassin Versant / Sous-bassins",
        strengths=[
            "Standard mondial pour l'ingénierie hydraulique, les barrages et l'aménagement des bassins versants"
        ],
        limitations=["Nécessite la délimitation préalable précise des sous-bassins"],
        references=["USACE (2021) HEC-HMS Technical Reference Manual"],
    ),
    "hec_ras": HydrologicalModelInfo(
        key="hec_ras",
        name="HEC-RAS (River Analysis System)",
        institution="US Army Corps of Engineers (USACE)",
        governing_equations="1D/2D Saint-Venant Shallow Water Equations (Unsteady Flow)",
        physics_type="Hydraulique 1D/2D à Surface Libre",
        typical_resolution="Grille 2D haute résolution (1 m à 10 m en zone inondable)",
        strengths=["Simulations ultra-précises d'inondation, d'expansions de crue et de ruptures de barrage"],
        limitations=["Exige une bathymétrie/MNT LiDAR très précis"],
        references=["Brunner (2020) HEC-RAS 2D User's Manual, USACE"],
    ),
    "vic": HydrologicalModelInfo(
        key="vic",
        name="VIC (Variable Infiltration Capacity Macroscale Hydrologic Model)",
        institution="University of Washington / Princeton University",
        governing_equations="Macroscale Energy-Water Balance avec courbe d'infiltration variable Sub-grid",
        physics_type="Macroscale Distributed Land Surface & Hydrology Model",
        typical_resolution="0.125° à 0.5° Grille Globale",
        strengths=["Intégration directe dans les modèles de climat mondial CMIP6 et la recherche hydrologique"],
        limitations=["Routage des cours d'eau géré par un module externe séparé (Lohmann routing)"],
        references=["Liang et al. (1994) J. Geophys. Res. 99, 14415-14428"],
    ),
}


class HydrologicalModelEngine:
    """Moteur de consultation des modèles numériques hydrologiques."""

    @classmethod
    def get_model(cls, key: str) -> HydrologicalModelInfo | None:
        return HYDROLOGICAL_MODELS_REGISTRY.get(key.lower())

    @classmethod
    def list_models(cls) -> list[str]:
        return list(HYDROLOGICAL_MODELS_REGISTRY.keys())
