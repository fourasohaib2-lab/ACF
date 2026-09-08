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
        """
        L'IA propose automatiquement le pack de couches scientifiques adaptées.

        NOTE (correction): situation was genuinely accepted and echoed,
        but the recommended_layers/justification below used to be a
        fixed cyclone-specific pack regardless of what situation was
        actually requested - recommend_for_situation("drought_detected")
        or ("blizzard_warning") got the identical "tropical cyclone
        tracking" pack and justification. Now only returns the real
        cyclone-specific pack for a genuinely cyclone-related situation
        (matching this class's own search()'s keyword-matching
        convention); honestly discloses no packaged recommendation
        otherwise, rather than mislabeling the cyclone pack as fitting
        an unrelated situation.
        """
        s = situation.lower()
        if "cyclone" in s or "hurricane" in s or "typhoon" in s:
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
        return {
            "situation": situation,
            "recommended_layers": [],
            "justification": "NOT_AVAILABLE_NO_CURATED_LAYER_PACK_FOR_THIS_SITUATION",
        }
