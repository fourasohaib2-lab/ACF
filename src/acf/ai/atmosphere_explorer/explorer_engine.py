"""
Atmospheric Complexity Framework (ACF)

AI-Assisted Atmosphere Explorer Engine Module (Phase 10)
(AIAtmosphereExplorer answering natural questions like 'Why is this storm intensifying?')
"""

from typing import Any


class AIAtmosphereExplorer:
    """
    Assistant IA pour la découverte et l'explication causale de la dynamique atmosphérique.
    """

    @classmethod
    def analyze_natural_query(cls, query_text: str = "Why is this storm intensifying?") -> dict[str, Any]:
        """
        Analyse une requête naturelle et retourne la chaîne explicative causale physique.

        NOTE (correction): this used to ignore query_text's content
        (beyond echoing it) and unconditionally claim a fabricated
        "Explosive Cyclogenesis" event, 5 fixed physical causes, a
        specific fake location (45.2°N, 12.4°W), and "96.8%"
        confidence for ANY query, regardless of what was actually
        asked - no real NLU/causal-attribution pipeline is connected
        here. Not fabricated.
        """
        return {
            "query": query_text,
            "detected_event": None,
            "physical_causes": [],
            "ai_confidence_score": None,
            "recommended_volume_slice": None,
            "status": "NOT_ANALYZED_NO_NLU_PIPELINE_CONNECTED",
            "is_real_data": False,
        }
