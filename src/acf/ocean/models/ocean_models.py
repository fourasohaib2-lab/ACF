"""
Atmospheric Complexity Framework (ACF)

Global Ocean Numerical Circulation Models Registry (Phase 5)
(HYCOM, NEMO, ROMS, MITgcm, SCHISM, ADCIRC, MOM6, FVCOM)
"""

from dataclasses import dataclass


@dataclass
class OceanModelInfo:
    """Description scientifique d'un modèle numérique de circulation océanique."""

    key: str
    name: str
    institution: str
    governing_equations: str
    vertical_coordinate: str  # e.g., "z-star", "Isopycnal", "Sigma", "Hybrid z-isopycnal"
    spatial_resolution: str
    strengths: list[str]
    limitations: list[str]
    references: list[str]


OCEAN_MODELS_REGISTRY: dict[str, OceanModelInfo] = {
    "nemo": OceanModelInfo(
        key="nemo",
        name="NEMO (Nucleus for European Modelling of the Ocean)",
        institution="NEMO European Consortium (CNRS, Mercator Ocean, Met Office, CMCC)",
        governing_equations="Primitive Equations Hydrostatiques Boussinesq",
        vertical_coordinate="z-star partielle / s-coordinate",
        spatial_resolution="1/12° Global (~9 km ORCA12) à 1/36° Régionale",
        strengths=["Modèle de référence européen pour Mercator Ocean, CMEMS et couplage climatiques EC-Earth/CNRM"],
        limitations=["Coût de calcul des grilles tripolaires ORCA"],
        references=["Madec et al. (2019) NEMO ocean engine, Scientific Notes ECMWF"],
    ),
    "hycom": OceanModelInfo(
        key="hycom",
        name="HYCOM (Hybrid Coordinate Ocean Model)",
        institution="US Navy / NOAA / NSSL / University of Miami",
        governing_equations="Primitive Equations avec coordonnées hybrides Isopycnales-Sigma-Z",
        vertical_coordinate="Hybrid Isopycnal / Sigma / Z-level",
        spatial_resolution="1/12° Global (~0.08°)",
        strengths=["Excellente représentation des couches de mélange et de la thermocline pycnocline"],
        limitations=["Transitions complexes entre couches isopycnales et z-levels près des côtes"],
        references=["Bleck (2002) Ocean Modelling 4, 55-70", "Chassignet et al. (2009)"],
    ),
    "roms": OceanModelInfo(
        key="roms",
        name="ROMS (Regional Ocean Modeling System)",
        institution="Rutgers University / UCLA",
        governing_equations="Free-surface, hydrostatic, primitive equations with S-coordinates",
        vertical_coordinate="Terrain-following S-coordinates (Sigma)",
        spatial_resolution="Haute résolution côtière (100 m à 1 km)",
        strengths=["Modélisation côtière ultra-précise, upwellings, estuaires et écoulements côtiers"],
        limitations=["Incertitudes de pression de gradient sur topographie abrupte"],
        references=["Shchepetkin & McWilliams (2005) Ocean Modelling 9, 347-404"],
    ),
}


class OceanModelEngine:
    """Moteur de consultation des modèles de circulation océanique."""

    @classmethod
    def get_model(cls, key: str) -> OceanModelInfo | None:
        return OCEAN_MODELS_REGISTRY.get(key.lower())

    @classmethod
    def list_models(cls) -> list[str]:
        return list(OCEAN_MODELS_REGISTRY.keys())
