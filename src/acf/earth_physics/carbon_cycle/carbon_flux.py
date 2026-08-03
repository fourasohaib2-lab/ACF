"""
Global Carbon Flux & Storage Model
"""

from typing import Dict


class GlobalCarbonFlux:
    """Modèle des flux mondiaux de carbone (Atmosphère <-> Océan <-> Végétation <-> Sol)."""

    @classmethod
    def get_annual_carbon_budget_gtc(cls) -> Dict[str, float]:
        return {
            "fossil_emissions_gtc_yr": 9.8,
            "land_use_change_gtc_yr": 1.2,
            "ocean_sink_gtc_yr": 2.8,
            "land_sink_gtc_yr": 3.4,
            "atmospheric_growth_gtc_yr": 4.8,
        }
