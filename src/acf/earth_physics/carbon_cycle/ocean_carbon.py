"""
Oceanic Carbon Absorption & Biological Pump Model
"""


class OceanCarbonBiologicalPump:
    """Modèle d'absorption océanique du $CO_2$ et de la pompe biologique de carbone."""

    @classmethod
    def ocean_co2_uptake_rate(cls, pco2_air: float, pco2_water: float, wind_speed_m_s: float) -> float:
        kw = 0.251 * (wind_speed_m_s**2)
        return kw * (pco2_air - pco2_water) * 0.001
