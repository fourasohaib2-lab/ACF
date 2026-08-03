"""
Vegetation Dynamics & LAI/NDVI Model
"""


class VegetationModel:
    """Modèle de dynamique de la végétation (LAI, NDVI, Biomasse)."""

    @classmethod
    def lai_from_ndvi(cls, ndvi: float) -> float:
        return max(0.0, (ndvi - 0.1) * 6.0)
