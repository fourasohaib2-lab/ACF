"""
Atmospheric Complexity Framework (ACF)

Scientific Layers Module (Raster, Vector, Contours, Wind Particle Flow, Isosurfaces & Radar/Satellite Renderers)
"""

from typing import Any, Dict, Optional


class BaseScientificLayer:
    """Classe de base pour toutes les couches scientifiques de visualisation ACF."""

    def __init__(self, layer_id: str, name: str, parameter_key: str, domain: str = "Atmosphère"):
        self.layer_id = layer_id
        self.name = name
        self.parameter_key = parameter_key
        self.domain = domain
        self.visible = True
        self.opacity = 1.0
        self.colormap = "viridis"
        self.vmin: Optional[float] = None
        self.vmax: Optional[float] = None

    def render(self) -> Dict[str, Any]:
        return {
            "id": self.layer_id,
            "name": self.name,
            "parameter": self.parameter_key,
            "domain": self.domain,
            "visible": self.visible,
            "opacity": self.opacity,
            "colormap": self.colormap,
            "range": [self.vmin, self.vmax],
        }


class RasterLayer(BaseScientificLayer):
    """Couche Raster d'un champ scalaire (Température, CAPE, Humidité, Pression)."""

    def __init__(self, layer_id: str, name: str, parameter_key: str, data_grid: Any = None):
        super().__init__(layer_id, name, parameter_key)
        self.data_grid = data_grid

    def render(self) -> Dict[str, Any]:
        info = super().render()
        info["type"] = "raster"
        info["grid_resolution"] = getattr(self.data_grid, "shape", (181, 360))
        return info


class ParticleFlowLayer(BaseScientificLayer):
    """Couche d'Animation de Flux de Particules de Vent (Style Earth Nullschool / Windy)."""

    def __init__(self, layer_id: str, name: str, u_grid: Any = None, v_grid: Any = None, num_particles: int = 5000):
        super().__init__(layer_id, name, parameter_key="wind_particle_flow", domain="Dynamique")
        self.u_grid = u_grid
        self.v_grid = v_grid
        self.num_particles = num_particles
        self.speed_scale = 1.0
        self.particle_lifetime_sec = 3.0

    def render(self) -> Dict[str, Any]:
        info = super().render()
        info["type"] = "particle_flow"
        info["num_particles"] = self.num_particles
        info["speed_scale"] = self.speed_scale
        return info


class IsosurfaceLayer(BaseScientificLayer):
    """Couche 3D d'Isosurface Iso-Valeur (ex: Tropopause à 2 PVU, Cœur de grêle à 35 dBZ)."""

    def __init__(self, layer_id: str, name: str, parameter_key: str, iso_value: float):
        super().__init__(layer_id, name, parameter_key, domain="3D Physics")
        self.iso_value = iso_value
        self.mesh_color = "#00FFFF"
        self.wireframe = False

    def render(self) -> Dict[str, Any]:
        info = super().render()
        info["type"] = "isosurface"
        info["iso_value"] = self.iso_value
        info["color"] = self.mesh_color
        return info


class RadarVolumeLayer(BaseScientificLayer):
    """Couche 3D de Rendu Volumique Radar (ZH Réflectivité, VR Vitesse Doppler, ZDR)."""

    def __init__(self, layer_id: str, name: str, radar_file: str, product: str = "ZH"):
        super().__init__(layer_id, name, parameter_key=f"radar_{product.lower()}", domain="Radar")
        self.radar_file = radar_file
        self.product = product  # "ZH", "VR", "ZDR", "KDP", "HCA"
        self.elevation_angles_deg = [0.5, 1.5, 2.4, 3.4, 5.0, 7.0, 10.0]

    def render(self) -> Dict[str, Any]:
        info = super().render()
        info["type"] = "radar_volume"
        info["product"] = self.product
        info["elevations"] = self.elevation_angles_deg
        return info


class SatelliteRGBLayer(BaseScientificLayer):
    """Couche Satellitaire d'Imagerie Multispectrale RGB (EUMETSAT / GOES-R)."""

    def __init__(self, layer_id: str, name: str, recipe: str = "Day_Natural"):
        super().__init__(layer_id, name, parameter_key="satellite_rgb", domain="Télédétection")
        self.recipe = recipe  # "Day_Natural", "Night_Microphysics", "Volcanic_Ash", "Dust_RGB", "Airmass"

    def render(self) -> Dict[str, Any]:
        info = super().render()
        info["type"] = "satellite_rgb"
        info["recipe"] = self.recipe
        return info
