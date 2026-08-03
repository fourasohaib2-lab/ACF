"""
Terrestrial Carbon Sink & NPP Model
"""


class TerrestrialCarbonSink:
    """Modèle du puits de carbone terrestre et de la production primaire nette (NPP)."""

    @classmethod
    def net_primary_productivity_gtc_yr(cls, temp_c: float, precip_mm: float) -> float:
        return max(0.0, 55.0 * (1.0 - (1.0 + (temp_c / 30.0)) ** -1))
