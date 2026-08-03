"""
Sea Ice Thermodynamics Model (Growth & Melt)
"""


class SeaIceThermodynamics:
    """Modèle thermodynamique de croissance et de fonte de la banquise (Stefan Growth Rule)."""

    @classmethod
    def ice_growth_rate_m_s(cls, surface_temp_c: float, freezing_temp_c: float = -1.8) -> float:
        if surface_temp_c >= freezing_temp_c:
            return 0.0
        return (freezing_temp_c - surface_temp_c) * 1.5e-8
