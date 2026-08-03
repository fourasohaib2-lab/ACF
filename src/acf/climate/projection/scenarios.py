"""
Atmospheric Complexity Framework (ACF)

CMIP6 & CORDEX Shared Socioeconomic Pathways (SSP) Climate Scenarios Module
(SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ClimateScenarioInfo:
    """Description d'un scénario de projection climatique CMIP6 / SSP."""
    key: str
    name: str
    forcing_2100_wm2: float
    projected_warming_2100_c: str
    co2_concentration_2100_ppm: float
    narrative: str
    policy_assumptions: str
    references: List[str]


SSP_SCENARIOS_REGISTRY: Dict[str, ClimateScenarioInfo] = {
    "ssp1_19": ClimateScenarioInfo(
        key="ssp1_19",
        name="SSP1-1.9 (Very Low Emissions / 1.5°C Goal)",
        forcing_2100_wm2=1.9,
        projected_warming_2100_c="1.0°C à 1.8°C (Moyenne 1.4°C)",
        co2_concentration_2100_ppm=390.0,
        narrative="Développement soutenable, neutralité carbone mondiale atteinte vers 2050.",
        policy_assumptions="Respect strict des accords de Paris pour contenir le réchauffement sous 1.5°C.",
        references=["IPCC AR6 WG1 Chapter 1", "Riahi et al. (2017) Glob. Environ. Change"],
    ),
    "ssp1_26": ClimateScenarioInfo(
        key="ssp1_26",
        name="SSP1-2.6 (Low Emissions / 2.0°C Goal)",
        forcing_2100_wm2=2.6,
        projected_warming_2100_c="1.3°C à 2.4°C (Moyenne 1.8°C)",
        co2_concentration_2100_ppm=440.0,
        narrative="Développement durable mondial, neutralité carbone atteinte dans la seconde moitié du XXIe siècle.",
        policy_assumptions="Forte transition énergétique et réduction rapide des gaz à effet de serre.",
        references=["IPCC AR6 WG1 Chapter 1"],
    ),
    "ssp2_45": ClimateScenarioInfo(
        key="ssp2_45",
        name="SSP2-4.5 (Middle of the Road)",
        forcing_2100_wm2=4.5,
        projected_warming_2100_c="2.1°C à 3.5°C (Moyenne 2.7°C)",
        co2_concentration_2100_ppm=600.0,
        narrative="Scénario intermédiaire poursuivant les tendances socio-économiques et énergétiques actuelles.",
        policy_assumptions="Réductions modérées des émissions de GES sans basculement radical.",
        references=["IPCC AR6 WG1 Chapter 1", "Fricko et al. (2017) Glob. Environ. Change"],
    ),
    "ssp3_70": ClimateScenarioInfo(
        key="ssp3_70",
        name="SSP3-7.0 (Regional Rivalry / High Emissions)",
        forcing_2100_wm2=7.0,
        projected_warming_2100_c="2.8°C à 4.6°C (Moyenne 3.6°C)",
        co2_concentration_2100_ppm=860.0,
        narrative="Rivalités régionales, faible coopération internationale et fortes émissions non régulées.",
        policy_assumptions="Investissements faibles dans l'efficacité énergétique et la protection de l'environnement.",
        references=["IPCC AR6 WG1 Chapter 1", "Fujimori et al. (2017) Glob. Environ. Change"],
    ),
    "ssp5_85": ClimateScenarioInfo(
        key="ssp5_85",
        name="SSP5-8.5 (Fossil-Fueled Development / Very High Emissions)",
        forcing_2100_wm2=8.5,
        projected_warming_2100_c="3.3°C à 5.7°C (Moyenne 4.4°C)",
        co2_concentration_2100_ppm=1135.0,
        narrative="Croissance basée sur l'exploitation intensive des énergies fossiles sans contrainte carbone.",
        policy_assumptions="Absence de politiques climatiques globales et consommation massive de charbon/pétrole.",
        references=["IPCC AR6 WG1 Chapter 1", "Kriegler et al. (2017) Glob. Environ. Change"],
    ),
}


class ClimateScenarioEngine:
    """Moteur de consultation des scénarios de projections climatiques CMIP6."""

    @classmethod
    def get(cls, key: str) -> Optional[ClimateScenarioInfo]:
        return SSP_SCENARIOS_REGISTRY.get(key.lower())

    @classmethod
    def list_scenarios(cls) -> List[str]:
        return list(SSP_SCENARIOS_REGISTRY.keys())
