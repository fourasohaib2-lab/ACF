"""
Soil Hydrology & Temperature Model
"""


class SoilModel:
    """Modèle à plusieurs couches de température et d'humidité du sol."""

    @classmethod
    def soil_moisture_index(cls, water_content_m3_m3: float, saturation_m3_m3: float = 0.45) -> float:
        return min(1.0, water_content_m3_m3 / saturation_m3_m3)
