"""
Atmospheric Complexity Framework (ACF)

Global Earth System & Climate Models Registry Module
(CESM2, EC-Earth3, MPI-ESM1.2, HadGEM3, NorESM2, GFDL-CM4, IPSL-CM6A, CNRM-CM6, SCREAM, ICON-ESM)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ClimateModelInfo:
    """Description scientifique complète d'un modèle du système Terre / Climat."""
    key: str
    name: str
    institution: str
    dynamical_core: str
    atmosphere_model: str
    ocean_model: str
    land_model: str
    sea_ice_model: str
    carbon_cycle: str
    coupler: str
    spatial_resolution: str
    strengths: List[str]
    limitations: List[str]
    references: List[str]


CLIMATE_MODELS_REGISTRY: Dict[str, ClimateModelInfo] = {
    "cesm2": ClimateModelInfo(
        key="cesm2",
        name="CESM2 (Community Earth System Model v2)",
        institution="NCAR / UCAR / NSF (USA)",
        dynamical_core="Finite Volume (FV) / Spectral Element (SE)",
        atmosphere_model="CAM6 (Community Atmosphere Model 6)",
        ocean_model="POP2 (Parallel Ocean Program) / MOM6",
        land_model="CLM5 (Community Land Model 5 with Biogeochemistry)",
        sea_ice_model="CICE5 (Community Ice Coders)",
        carbon_cycle="Explicite (Interactive Carbon-Nitrogen Cycle)",
        coupler="CPL7 / CIME (Coupled Infrastructure for Modeling the Earth)",
        spatial_resolution="1.0° (Atmosphere ~100 km, Ocean ~30-100 km)",
        strengths=["Physique du sol CLM5 ultra-détaillée, réponse climatique équilibrée ECS = 5.2 K"],
        limitations=["Sensibilité climatique élevée pouvant surestimer le réchauffement du XXe siècle"],
        references=["Danabasoglu et al. (2020) J. Adv. Model. Earth Syst. 12, e2019MS001916"],
    ),
    "ec_earth3": ClimateModelInfo(
        key="ec_earth3",
        name="EC-Earth3 (European Earth System Model)",
        institution="EC-Earth Consortium (27 European Research Institutes)",
        dynamical_core="IFS Spectral Hydrostatic Core",
        atmosphere_model="IFS Cy36r4 (ECMWF Integrated Forecasting System)",
        ocean_model="NEMO v3.6 (Nucleus for European Modelling of the Ocean)",
        land_model="HTESSEL (Hydrology Tiled ECMWF Scheme for Surface Exchanges over Land)",
        sea_ice_model="LIM3 (Louvain-la-Neuve Sea Ice Model)",
        carbon_cycle="TM5 (Atmosphere Chemistry & Transport) / PISCES",
        coupler="OASIS3-MCT",
        spatial_resolution="T255 (~80 km Atmosphere, 1.0° / 0.25° Ocean)",
        strengths=["Basé sur le modèle prévisionnel opérationnel IFS d'ECMWF, excellente dynamique synoptique"],
        limitations=["Coût de calcul élevé des modules de chimie atmosphérique TM5"],
        references=["Döscher et al. (2022) Geosci. Model Dev. 15, 2973-3020"],
    ),
    "mpi_esm1_2": ClimateModelInfo(
        key="mpi_esm1_2",
        name="MPI-ESM1.2 (Max Planck Institute Earth System Model)",
        institution="Max Planck Institute for Meteorology (Germany)",
        dynamical_core="Spectral Atmospheric Core",
        atmosphere_model="ECHAM6.3",
        ocean_model="MPIOM (MPI Ocean Model)",
        land_model="JSBACH3.2 (Dynamic Vegetation & Land Surface)",
        sea_ice_model="MPIOM Sea Ice Module",
        carbon_cycle="HAMOCC (Hamburg Ocean Carbon Cycle)",
        coupler="OASIS3-MCT",
        spatial_resolution="T63 (~200 km) / T127 (~100 km)",
        strengths=["Excellente conservation de la masse et de l'énergie, très stable sur les millénaires"],
        limitations=["Résolution atmosphérique moyenne en mode standard CMIP6"],
        references=["Mauritsen et al. (2019) J. Adv. Model. Earth Syst. 11, 998-1038"],
    ),
    "cnrm_cm6": ClimateModelInfo(
        key="cnrm_cm6",
        name="CNRM-CM6-1 (Météo-France / CERFACS)",
        institution="CNRM (Météo-France) / CERFACS (France)",
        dynamical_core="ARPEGE Spectral Core",
        atmosphere_model="ARPEGE-Climat v6.3",
        ocean_model="NEMO v3.6",
        land_model="SURFEX v8.0 (ISBA-CTRIP Hydro-Vegetation)",
        sea_ice_model="GELATO v6",
        carbon_cycle="PISCES v2 (Ocean Biogeochemistry)",
        coupler="OASIS3-MCT",
        spatial_resolution="T127 (~140 km Atmosphere, 1.0° Ocean)",
        strengths=["Représentation très précise de la mousson et du schéma de surface SURFEX"],
        limitations=["Biais froid persistant sur l'Océan Austral"],
        references=["Voldoire et al. (2019) J. Adv. Model. Earth Syst. 11, 2177-2213"],
    ),
    "scream": ClimateModelInfo(
        key="scream",
        name="SCREAM (Simple Cloud-Resolving E3SM Atmosphere Model)",
        institution="US Department of Energy (DOE / LLNL / LBNL)",
        dynamical_core="Non-hydrostatic Spectral Element (SE) Homme",
        atmosphere_model="SCREAM Cloud-Resolving Model (3 km Global)",
        ocean_model="MPAS-Ocean (Model for Prediction Across Scales)",
        land_model="ELM (E3SM Land Model)",
        sea_ice_model="MPAS-SeaIce",
        carbon_cycle="Interactive Bio-Geo-Chemistry",
        coupler="CIME / MOAB",
        spatial_resolution="3.2 km Global Non-Hydrostatic Grid",
        strengths=["Résolution explicite de la convection profonde globale sans paramétrisation convective!"],
        limitations=["Extrêmement gourmand en supercalculateurs Exascale"],
        references=["Caldwell et al. (2021) Geosci. Model Dev. 14, 3963-4011"],
    ),
}


class ClimateModelEngine:
    """Moteur de consultation des modèles du Système Terre."""

    @classmethod
    def get_model(cls, key: str) -> Optional[ClimateModelInfo]:
        return CLIMATE_MODELS_REGISTRY.get(key.lower())

    @classmethod
    def list_models(cls) -> List[str]:
        return list(CLIMATE_MODELS_REGISTRY.keys())
