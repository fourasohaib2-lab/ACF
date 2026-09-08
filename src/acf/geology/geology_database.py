"""
Atmospheric Complexity Framework (ACF)

Global Geology Database & Internal Earth Structure Module (Phase 1)
(Crust, Upper/Lower Mantle, Outer/Inner Core, Density, Temperature, Pressure, Wave Velocities)
"""

from dataclasses import dataclass


@dataclass
class EarthLayer:
    """Description d'une couche interne de la Terre (modèle PREM)."""

    name: str
    depth_top_km: float
    depth_bottom_km: float
    thickness_km: float
    density_g_cm3: float
    temperature_k: float
    pressure_gpa: float
    composition: str
    vp_km_s: float
    vs_km_s: float
    references: list[str]


EARTH_LAYERS_PREM: dict[str, EarthLayer] = {
    "continental_crust": EarthLayer(
        name="Continental Crust",
        depth_top_km=0.0,
        depth_bottom_km=35.0,
        thickness_km=35.0,
        density_g_cm3=2.7,
        temperature_k=600.0,
        pressure_gpa=1.0,
        composition="Granitic / Andesitic Rocks (Si-Al)",
        vp_km_s=6.3,
        vs_km_s=3.6,
        references=["Dziewonski & Anderson (1981) PREM"],
    ),
    "oceanic_crust": EarthLayer(
        name="Oceanic Crust",
        depth_top_km=0.0,
        depth_bottom_km=7.0,
        thickness_km=7.0,
        density_g_cm3=3.0,
        temperature_k=500.0,
        pressure_gpa=0.2,
        composition="Basaltic / Gabbroic Rocks (Si-Ma)",
        vp_km_s=6.8,
        vs_km_s=3.9,
        references=["PREM Model"],
    ),
    "upper_mantle": EarthLayer(
        name="Upper Mantle (Asthenosphere)",
        depth_top_km=35.0,
        depth_bottom_km=670.0,
        thickness_km=635.0,
        density_g_cm3=3.4,
        temperature_k=1600.0,
        pressure_gpa=24.0,
        composition="Peridotite / Olivine / Pyroxene",
        vp_km_s=8.1,
        vs_km_s=4.5,
        references=["PREM Model"],
    ),
    "lower_mantle": EarthLayer(
        name="Lower Mantle (Mesosphere)",
        depth_top_km=670.0,
        depth_bottom_km=2890.0,
        thickness_km=2220.0,
        density_g_cm3=4.4,
        temperature_k=2500.0,
        pressure_gpa=135.0,
        composition="Bridgmanite / Ferropericlase",
        vp_km_s=11.0,
        vs_km_s=6.2,
        references=["PREM Model"],
    ),
    "outer_core": EarthLayer(
        name="Outer Core (Liquid)",
        depth_top_km=2890.0,
        depth_bottom_km=5150.0,
        thickness_km=2260.0,
        density_g_cm3=11.0,
        temperature_k=4500.0,
        pressure_gpa=330.0,
        composition="Liquid Iron-Nickel Alloy (Fe-Ni)",
        vp_km_s=9.0,
        vs_km_s=0.0,  # Pas d'ondes S dans les liquides
        references=["PREM Model"],
    ),
    "inner_core": EarthLayer(
        name="Inner Core (Solid)",
        depth_top_km=5150.0,
        depth_bottom_km=6371.0,
        thickness_km=1221.0,
        density_g_cm3=13.0,
        temperature_k=5700.0,
        pressure_gpa=360.0,
        composition="Solid Crystalline Iron-Nickel",
        vp_km_s=11.2,
        vs_km_s=3.6,
        references=["PREM Model"],
    ),
}


class GeologyDatabase:
    """Base de données et registre de la structure interne de la Terre et des couches géologiques."""

    @classmethod
    def get_layer(cls, key: str) -> EarthLayer | None:
        return EARTH_LAYERS_PREM.get(key.lower())

    @classmethod
    def list_layers(cls) -> list[str]:
        return list(EARTH_LAYERS_PREM.keys())
