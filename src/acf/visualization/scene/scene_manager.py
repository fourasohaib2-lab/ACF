"""
Atmospheric Complexity Framework (ACF)

Visualization Scene Manager (2D, 3D Globe & 4D Scene Container)
"""

from typing import Any
from uuid import uuid4


class VisualizationScene:
    """
    Gestionnaire de Scène Graphique 2D / 3D Globe / 4D Temps.
    """

    def __init__(self, name: str = "Default AWCI Scene", mode: str = "2D"):
        self.scene_id = str(uuid4())
        self.name = name
        self.mode = mode  # "2D", "3D_Globe", "4D_Time"
        self.layers: list[dict[str, Any]] = []
        self.camera_state = {"mode": "Perspective", "zoom": 1.0, "lat": 0.0, "lon": 0.0, "altitude_km": 1000.0}
        self.active_time = "2026-07-30T12:00:00Z"
        self.active_vertical_level = "surface"  # "500hPa", "300hPa", "surface"

    def add_layer(
        self, layer_id: str, name: str, layer_type: str, data: Any = None, opacity: float = 1.0, visible: bool = True
    ) -> dict[str, Any]:
        """Ajoute une couche scientifique à la scène."""
        layer = {
            "id": layer_id,
            "name": name,
            "type": layer_type,  # "raster", "vector", "contour", "wind_particles", "isosurface", "radar_volume"
            "data": data,
            "opacity": opacity,
            "visible": visible,
            "z_index": len(self.layers),
        }
        self.layers.append(layer)
        return layer

    def remove_layer(self, layer_id: str):
        """Supprime une couche de la scène."""
        self.layers = [layer_item for layer_item in self.layers if layer_item["id"] != layer_id]

    def set_layer_visibility(self, layer_id: str, visible: bool):
        """Active ou désactive la visibilité d'une couche."""
        for layer in self.layers:
            if layer["id"] == layer_id:
                layer["visible"] = visible

    def set_layer_opacity(self, layer_id: str, opacity: float):
        """Ajuste l'opacité d'une couche (0.0 à 1.0)."""
        for layer in self.layers:
            if layer["id"] == layer_id:
                layer["opacity"] = max(0.0, min(1.0, opacity))

    def get_layer(self, layer_id: str) -> dict[str, Any] | None:
        """Récupère une couche par son ID."""
        for layer in self.layers:
            if layer["id"] == layer_id:
                return layer
        return None

    def render_summary(self) -> dict[str, Any]:
        """Résumé synthétique de l'état de rendu de la scène."""
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "mode": self.mode,
            "total_layers": len(self.layers),
            "visible_layers": len([layer_item for layer_item in self.layers if layer_item["visible"]]),
            "camera": self.camera_state,
            "time": self.active_time,
            "level": self.active_vertical_level,
        }
