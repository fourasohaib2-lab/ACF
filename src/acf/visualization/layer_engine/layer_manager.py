"""
Atmospheric Complexity Framework (ACF)

Scientific Layer Stack & Active View Manager Module
(LayerManager managing active view layer stack, opacity, lock, drag & drop, and uncertainty)
"""

from typing import Any

from acf.visualization.layer_engine.layer_metadata import LayerDefinition
from acf.visualization.layer_engine.layer_registry import LayerRegistry


class LayerManager:
    """
    Gestionnaire centralisé de la pile de couches (Active View Layer Stack) d'ACF v1.0.
    """

    def __init__(self):
        self.active_stack: list[LayerDefinition] = []

    def add_to_stack(self, layer_id: str) -> LayerDefinition | None:
        """Ajoute une couche à la pile de vue active."""
        layer = LayerRegistry.get_layer(layer_id)
        if layer and layer not in self.active_stack:
            self.active_stack.append(layer)
            return layer
        return None

    def remove_from_stack(self, layer_id: str) -> bool:
        """Retire une couche de la pile."""
        self.active_stack = [item for item in self.active_stack if item.layer_id != layer_id]
        return True

    def reorder_stack(self, new_order_layer_ids: list[str]) -> list[LayerDefinition]:
        """Réordonne l'ordre d'affichage de la pile (de fond en comble)."""
        reordered = []
        for lid in new_order_layer_ids:
            layer = LayerRegistry.get_layer(lid)
            if layer:
                reordered.append(layer)
        self.active_stack = reordered
        return self.active_stack

    def get_stack_summary(self) -> dict[str, Any]:
        """Retourne la synthèse de la pile de vue active."""
        return {
            "active_layers_count": len(self.active_stack),
            "layers": [item.to_dict() for item in self.active_stack],
            "top_layer": self.active_stack[-1].layer_id if self.active_stack else None,
        }
