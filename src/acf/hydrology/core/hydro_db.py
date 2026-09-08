"""
Atmospheric Complexity Framework (ACF)

Global Hydrology Database & Watershed Core Module (Phase 1)
(Watersheds, Drainage Basins, Hydraulic Radius, Water Balance Equation)
"""

from dataclasses import dataclass


@dataclass
class WatershedInfo:
    """Description scientifique d'un bassin versant / bassin hydrographique."""

    watershed_id: str
    name: str  # e.g., "Bassin de la Seine"
    major_river: str  # "Seine"
    area_km2: float
    main_channel_length_km: float
    average_slope_m_km: float
    land_use_types: list[str]
    tributaries: list[str]


WATERSHED_REGISTRY: dict[str, WatershedInfo] = {
    "seine_basin": WatershedInfo(
        watershed_id="seine_basin",
        name="Bassin Versant de la Seine",
        major_river="Seine",
        area_km2=78650.0,
        main_channel_length_km=777.0,
        average_slope_m_km=0.6,
        land_use_types=["Agriculture", "Forest", "Urban"],
        tributaries=["Marne", "Oise", "Yonne", "Aube"],
    ),
    "rhine_basin": WatershedInfo(
        watershed_id="rhine_basin",
        name="Rhine River Basin",
        major_river="Rhine",
        area_km2=185000.0,
        main_channel_length_km=1230.0,
        average_slope_m_km=1.2,
        land_use_types=["Forest", "Alpine Snowmelt", "Agriculture", "Industrial"],
        tributaries=["Main", "Moselle", "Neckar", "Aare"],
    ),
}


class HydrologyDatabase:
    """Base de données et moteur d'équations hydrologiques fondamentales."""

    @staticmethod
    def hydraulic_radius_m(wetted_area_m2: float, wetted_perimeter_m: float) -> float:
        """Calcul du rayon hydraulique Rh = A / P (mètres)."""
        if wetted_perimeter_m <= 0.0:
            return 0.0
        return wetted_area_m2 / wetted_perimeter_m

    @staticmethod
    def water_balance(precipitation_mm: float, evapotranspiration_mm: float, runoff_mm: float) -> float:
        """Calcul du bilan hydrique Delta S = P - E - Q (mm)."""
        return precipitation_mm - evapotranspiration_mm - runoff_mm

    @classmethod
    def get_watershed(cls, key: str) -> WatershedInfo | None:
        return WATERSHED_REGISTRY.get(key.lower())

    @classmethod
    def list_watersheds(cls) -> list[str]:
        return list(WATERSHED_REGISTRY.keys())
