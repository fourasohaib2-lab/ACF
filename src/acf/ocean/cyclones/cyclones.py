"""
Atmospheric Complexity Framework (ACF)

Tropical Cyclones, Hurricanes & IBTrACS Best Track Module (Phase 4)
(Saffir-Simpson Scale 1-5, NHC / JTWC Track, Forecast Cone, Rapid Intensification)
"""

from dataclasses import dataclass


@dataclass
class TropicalCycloneInfo:
    """Description et trajectoire d'un cyclone tropical / ouragan / typhon."""

    cyclone_id: str  # e.g., "AL092024"
    name: str  # e.g., "Hélène"
    basin: str  # "North Atlantic", "Western Pacific", "Indian Ocean"
    category_saffir_simpson: int  # 0 (Tropical Storm), 1 à 5
    max_sustained_wind_kt: float
    min_central_pressure_hpa: float
    radius_max_wind_nm: float
    current_lat: float
    current_lon: float
    movement_dir_deg: float
    movement_speed_kt: float
    rapid_intensification_flag: bool


class HurricaneDatabase:
    """Base de données et moteur de suivi des cyclones tropicaux mondiaux."""

    @staticmethod
    def saffir_simpson_category(wind_speed_kt: float) -> int:
        """Détermine la catégorie Saffir-Simpson (1 à 5) d'après la vitesse maximale du vent soutenu sur 1 minute."""
        if wind_speed_kt < 64.0:
            return 0  # Tempête tropicale / Dépression
        elif wind_speed_kt < 83.0:
            return 1
        elif wind_speed_kt < 96.0:
            return 2
        elif wind_speed_kt < 113.0:
            return 3
        elif wind_speed_kt < 137.0:
            return 4
        else:
            return 5

    @classmethod
    def get_active_cyclones(cls) -> list[TropicalCycloneInfo]:
        """
        Retourne la liste des cyclones tropicaux actifs dans le monde.

        NOTE (correction — operationally dangerous): this used to
        unconditionally claim a specific Category 4 hurricane named
        "Helene" (reusing the name of a real, historically destructive
        2024 Atlantic hurricane) was currently active, complete with
        realistic-looking position (24.5N, -84.2W), pressure (938 hPa),
        and a rapid-intensification flag, for ANY call with 0
        parameters and no real NHC/JTWC best-track feed ever connected.
        A caller checking "active cyclones" during a genuinely quiet
        period would be told a major hurricane was underway. Not
        fabricated.
        """
        return []
