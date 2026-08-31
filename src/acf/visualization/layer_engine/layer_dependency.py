"""
Atmospheric Complexity Framework (ACF)

Layer Dependency Graph Module
(LayerDependencyGraph building DAG physics dependencies for automatic calculation and AI explanation)
"""

from typing import Any

from acf.visualization.layer_engine.layer_registry import LayerRegistry


class LayerDependencyGraph:
    """Graphe orienté acyclique (DAG) de dépendance entre couches scientifiques."""

    @classmethod
    def get_layer_dependencies(cls, layer_id: str) -> list[str]:
        layer = LayerRegistry.get_layer(layer_id)
        return layer.dependencies if layer else []

    @classmethod
    def build_causal_tree(cls, target_layer_id: str) -> dict[str, Any]:
        deps = cls.get_layer_dependencies(target_layer_id)
        return {
            "target_layer": target_layer_id,
            "upstream_dependencies": deps,
            "causal_chain": f"{' -> '.join(deps)} -> {target_layer_id}" if deps else target_layer_id,
        }
