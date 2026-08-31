"""
Atmospheric Complexity Framework (ACF)

Scientific Layer Search & AI Layer Advisor Engine Module
"""

from typing import Any

from acf.visualization.layer_engine.layer_registry import LayerRegistry


class LayerSearchEngine:
    """Moteur de recherche scientifique et de recommandations d'IA de couches."""

    @classmethod
    def search(cls, query_text: str) -> list[dict[str, Any]]:
        q = query_text.lower()
        if "thunderstorm" in q or "orage" in q:
            layers = [
                LayerRegistry.get_layer("conv.cape"),
                LayerRegistry.get_layer("thermo.theta_e"),
            ]
            return [lyr.to_dict() for lyr in layers if lyr is not None]
        return [item.to_dict() for item in LayerRegistry.list_all_layers()]

    @classmethod
    def recommend_for_situation(cls, situation: str = "cyclone_detected") -> dict[str, Any]:
        """L'IA propose automatiquement le pack de couches scientifiques adaptées."""
        return {
            "situation": situation,
            "recommended_layers": [
                "ocean.sst",
                "atm.vorticity.500hpa",
                "conv.cape",
                "atm.temperature.850hpa",
                "hydro.river_discharge",
            ],
            "justification": "Optimal multi-sphere diagnostic pack for tropical cyclone tracking and coastal impact.",
        }
