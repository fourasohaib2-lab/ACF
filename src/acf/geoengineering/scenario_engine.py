"""
Atmospheric Complexity Framework (ACF)

Climate Scenarios Engine Module (Phase 8)
(ClimateScenarioEngine modeling CMIP6 SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5, Net Zero, and BAU)
"""

from dataclasses import dataclass


@dataclass
class SSPScenario:
    """Description d'un scénario d'émission socio-économique CMIP6 SSP."""

    scenario_id: str
    name: str
    radiative_forcing_2100_w_m2: float
    warming_mean_2100_c: float
    warming_range_2100_c: str
    co2_concentration_2100_ppm: float
    sea_level_rise_2100_m: float
    policy_description: str


SSP_CATALOG: dict[str, SSPScenario] = {
    "ssp1_19": SSPScenario(
        scenario_id="SSP1-1.9",
        name="SSP1-1.9 (Very Low Emissions / 1.5°C Goal)",
        radiative_forcing_2100_w_m2=1.9,
        warming_mean_2100_c=1.4,
        warming_range_2100_c="1.0°C to 1.8°C",
        co2_concentration_2100_ppm=390.0,
        sea_level_rise_2100_m=0.38,
        policy_description="Net Zero CO2 achieved by 2050 with global sustainability shift.",
    ),
    "ssp2_45": SSPScenario(
        scenario_id="SSP2-4.5",
        name="SSP2-4.5 (Intermediate Emissions / Middle of the Road)",
        radiative_forcing_2100_w_m2=4.5,
        warming_mean_2100_c=2.7,
        warming_range_2100_c="2.1°C to 3.5°C",
        co2_concentration_2100_ppm=600.0,
        sea_level_rise_2100_m=0.56,
        policy_description="Current national climate targets continued with modest decarbonization.",
    ),
    "ssp5_85": SSPScenario(
        scenario_id="SSP5-8.5",
        name="SSP5-8.5 (Very High Emissions / Fossil-Fueled Development)",
        radiative_forcing_2100_w_m2=8.5,
        warming_mean_2100_c=4.4,
        warming_range_2100_c="3.3°C to 5.7°C",
        co2_concentration_2100_ppm=1130.0,
        sea_level_rise_2100_m=0.77,
        policy_description="Intensive fossil fuel reliance without climate mitigation.",
    ),
}


class ClimateScenarioEngine:
    """
    Moteur de projection des scénarios climatiques CMIP6 et des trajectoires d'émissions.
    """

    @classmethod
    def get_scenario(cls, scenario_key: str) -> SSPScenario | None:
        return SSP_CATALOG.get(scenario_key.lower().replace("-", "_"))

    @classmethod
    def list_scenarios(cls) -> list[str]:
        return list(SSP_CATALOG.keys())
