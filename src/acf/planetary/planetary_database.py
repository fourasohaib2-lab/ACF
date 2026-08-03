"""
Atmospheric Complexity Framework (ACF)

Global Planetary Defense Center & Near-Earth Objects Registry Module (Phase 1)
(NearEarthObject, PotentialHazard, ImpactScenario, PlanetaryDefenseRegistry, PHAs: Apophis, Bennu, Chicxulub)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class NearEarthObject:
    """Description d'un objet géocroiseur (NEO / PHA)."""
    neo_id: str
    name: str
    object_class: str  # Apollo, Aten, Amor, Atira, Comet
    diameter_m: float
    mass_kg: float
    density_g_cm3: float
    albedo: float
    semi_major_axis_au: float
    eccentricity: float
    inclination_deg: float
    moid_au: float  # Minimum Orbit Intersection Distance (AU)
    velocity_km_s: float
    kinetic_energy_joules: float
    impact_probability: float
    is_potentially_hazardous: bool
    discovery_agency: str
    references: List[str]


@dataclass
class PotentialHazard:
    """Évaluation de risque de géocroiseur à haut potentiel de danger (PHA)."""
    neo_id: str
    torino_scale_level: int  # 0 to 10
    palermo_scale_score: float
    next_close_approach_date: str
    min_distance_ld: float  # Distance en distances lunaires (LD)


@dataclass
class ImpactScenario:
    """Scénario d'impact cosmique historique ou prédictif."""
    scenario_name: str
    impactor_name: str
    diameter_m: float
    velocity_km_s: float
    kinetic_energy_megatons_tnt: float
    target_environment: str  # Ocean, Continental Crust, Upper Atmosphere
    crater_diameter_km: float
    global_extinction_risk: bool


NEO_REGISTRY: Dict[str, NearEarthObject] = {
    "apophis": NearEarthObject(
        neo_id="99942",
        name="99942 Apophis",
        object_class="Aten",
        diameter_m=370.0,
        mass_kg=6.1e10,
        density_g_cm3=2.6,
        albedo=0.33,
        semi_major_axis_au=0.922,
        eccentricity=0.191,
        inclination_deg=3.33,
        moid_au=0.00025,
        velocity_km_s=30.7,
        kinetic_energy_joules=2.8e19,  # ~670 Megatons TNT
        impact_probability=0.0,  # Éliminé pour 2029/2036/2068
        is_potentially_hazardous=True,
        discovery_agency="NASA / JPL CNEOS",
        references=["JPL Small-Body Database", "NASA PDCO Manual"],
    ),
    "bennu": NearEarthObject(
        neo_id="101955",
        name="101955 Bennu",
        object_class="Apollo",
        diameter_m=492.0,
        mass_kg=7.3e10,
        density_g_cm3=1.19,
        albedo=0.044,
        semi_major_axis_au=1.126,
        eccentricity=0.203,
        inclination_deg=6.03,
        moid_au=0.0033,
        velocity_km_s=28.0,
        kinetic_energy_joules=2.86e19,  # ~1200 Megatons TNT
        impact_probability=0.00037,  # 1/2700 d'ici 2300
        is_potentially_hazardous=True,
        discovery_agency="NASA OSIRIS-REx / LINEAR",
        references=["Lauretta et al. (2019) Science", "Farnocchia et al. (2021) Icarus"],
    ),
    "chicxulub_impactor": NearEarthObject(
        neo_id="IMPACTOR-KPG",
        name="Chicxulub Asteroid (K-Pg Extinction)",
        object_class="Apollo / Carbonaceous Chondrite",
        diameter_m=10000.0,  # 10 km
        mass_kg=1.0e15,
        density_g_cm3=2.5,
        albedo=0.05,
        semi_major_axis_au=1.5,
        eccentricity=0.4,
        inclination_deg=15.0,
        moid_au=0.0,
        velocity_km_s=20.0,
        kinetic_energy_joules=2.0e24,  # ~100 Million Megatons TNT
        impact_probability=1.0,  # Impact survenu il y a 66 Ma
        is_potentially_hazardous=True,
        discovery_agency="Alvarez et al. (1980) / USGS",
        references=["Alvarez et al. (1980) Science", "Schulte et al. (2010) Science"],
    ),
}


class PlanetaryDefenseRegistry:
    """Registre de défense planétaire des astéroïdes et comètes géocroiseurs."""

    @classmethod
    def get_neo(cls, key: str) -> Optional[NearEarthObject]:
        return NEO_REGISTRY.get(key.lower())

    @classmethod
    def list_neos(cls) -> List[str]:
        return list(NEO_REGISTRY.keys())


class PlanetaryDatabase:
    """Base de données planétaire et des objets géocroiseurs."""

    @classmethod
    def get_sample_hazard(cls, neo_key: str = "bennu") -> PotentialHazard:
        return PotentialHazard(
            neo_id=neo_key,
            torino_scale_level=1,
            palermo_scale_score=-1.4,
            next_close_approach_date="2182-09-24",
            min_distance_ld=1.8,
        )
