"""
Atmospheric Complexity Framework (ACF)

Planetary Atmospheres Engine Module (Phase 5)
(PlanetaryAtmosphereEngine modeling Earth, Mars, Venus, Mercury, Jupiter, Saturn, Uranus, Neptune, Titan)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


R_GAS_CONST = 8.314462618  # J / (mol K)


@dataclass
class PlanetaryAtmosphere:
    """Propriétés physiques de l'atmosphère d'un corps du Système Solaire."""
    planet_name: str
    surface_pressure_pa: float
    surface_gravity_m_s2: float
    mean_temperature_k: float
    mean_molar_mass_kg_mol: float
    scale_height_km: float
    bond_albedo: float
    major_gases: Dict[str, float]  # Nom gaz -> % volumique
    cloud_layers: List[str]
    max_wind_speed_m_s: float
    prominent_storms: List[str]


PLANET_ATMOSPHERES: Dict[str, PlanetaryAtmosphere] = {
    "earth": PlanetaryAtmosphere(
        planet_name="Earth",
        surface_pressure_pa=101325.0,
        surface_gravity_m_s2=9.80665,
        mean_temperature_k=288.15,
        mean_molar_mass_kg_mol=0.02897,
        scale_height_km=8.5,
        bond_albedo=0.306,
        major_gases={"N2": 78.08, "O2": 20.95, "Ar": 0.93, "CO2": 0.042},
        cloud_layers=["Tropospheric Water Clouds", "Polar Stratospheric Clouds"],
        max_wind_speed_m_s=110.0,
        prominent_storms=["Tropical Cyclones", "Mid-Latitude Synoptic Lows"],
    ),
    "mars": PlanetaryAtmosphere(
        planet_name="Mars",
        surface_pressure_pa=610.0,  # ~6.1 mbar
        surface_gravity_m_s2=3.7207,
        mean_temperature_k=210.0,
        mean_molar_mass_kg_mol=0.04334,
        scale_height_km=11.1,
        bond_albedo=0.25,
        major_gases={"CO2": 95.32, "N2": 2.7, "Ar": 1.6, "O2": 0.13},
        cloud_layers=["CO2 Ice Clouds", "Water-Ice Cirrus Clouds", "Dust Clouds"],
        max_wind_speed_m_s=40.0,
        prominent_storms=["Global Planet-Encircling Dust Storms"],
    ),
    "venus": PlanetaryAtmosphere(
        planet_name="Venus",
        surface_pressure_pa=9.2e6,  # 92 bar
        surface_gravity_m_s2=8.87,
        mean_temperature_k=737.0,  # 464°C (Greenhouse effect)
        mean_molar_mass_kg_mol=0.04345,
        scale_height_km=15.9,
        bond_albedo=0.77,
        major_gases={"CO2": 96.5, "N2": 3.5, "SO2": 0.015},
        cloud_layers=["Sulfuric Acid Cloud Deck (48-65 km)"],
        max_wind_speed_m_s=100.0,
        prominent_storms=["Super-Rotating Zonal Winds", "Polar Vortices"],
    ),
    "jupiter": PlanetaryAtmosphere(
        planet_name="Jupiter",
        surface_pressure_pa=1.0e5,  # 1 bar reference
        surface_gravity_m_s2=24.79,
        mean_temperature_k=165.0,  # at 1 bar
        mean_molar_mass_kg_mol=0.00222,
        scale_height_km=27.0,
        bond_albedo=0.343,
        major_gases={"H2": 89.8, "He": 10.2, "CH4": 0.3, "NH3": 0.02},
        cloud_layers=["Ammonia Ice Clouds", "Ammonium Hydrosulfide Clouds", "Water Ice Clouds"],
        max_wind_speed_m_s=150.0,
        prominent_storms=["Great Red Spot", "Oval BA (Red Spot Jr)"],
    ),
    "titan": PlanetaryAtmosphere(
        planet_name="Titan",
        surface_pressure_pa=146700.0,  # 1.45 bar
        surface_gravity_m_s2=1.352,
        mean_temperature_k=93.7,
        mean_molar_mass_kg_mol=0.028,
        scale_height_km=40.0,
        bond_albedo=0.22,
        major_gases={"N2": 98.4, "CH4": 1.4, "H2": 0.2},
        cloud_layers=["Methane Ice Clouds", "Photochemical Organic Haze Layer"],
        max_wind_speed_m_s=20.0,
        prominent_storms=["Polar Methane Rain Storms"],
    ),
}


class PlanetaryAtmosphereEngine:
    """
    Moteur d'étude comparative des atmosphères planétaires du Système Solaire.
    """

    @classmethod
    def get_atmosphere(cls, planet_name: str) -> Optional[PlanetaryAtmosphere]:
        return PLANET_ATMOSPHERES.get(planet_name.lower())

    @classmethod
    def calculate_scale_height_km(cls, temperature_k: float, molar_mass_kg_mol: float, gravity_m_s2: float) -> float:
        """
        Calcule la hauteur d'échelle atmosphérique : H = (R * T) / (M * g)
        
        Equations:
            H = \\frac{R \\cdot T}{M \\cdot g}
        """
        h_m = (R_GAS_CONST * temperature_k) / (molar_mass_kg_mol * gravity_m_s2)
        return h_m / 1000.0
