"""
Global Carbon Flux & Storage Model
"""


class GlobalCarbonFlux:
    """Modèle des flux mondiaux de carbone (Atmosphère <-> Océan <-> Végétation <-> Sol)."""

    @classmethod
    def get_annual_carbon_budget_gtc(cls) -> dict[str, float | bool]:
        """
        Global annual carbon budget (GtC/yr).

        NOTE: takes no inputs and has no live data feed connected -
        these are plausible illustrative values (comparable in order
        of magnitude to recent Global Carbon Project estimates) but
        are NOT computed or fetched from real data. Marked explicitly
        rather than presented as if live/measured.
        """
        return {
            "fossil_emissions_gtc_yr": 9.8,
            "land_use_change_gtc_yr": 1.2,
            "ocean_sink_gtc_yr": 2.8,
            "land_sink_gtc_yr": 3.4,
            "atmospheric_growth_gtc_yr": 4.8,
            "is_real_data": False,
        }
