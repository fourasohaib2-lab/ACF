"""
Atmospheric Complexity Framework (ACF)

XAI Explanation Engine Visualization Adapter Module
"""

from typing import Any


class XAIExplanationEngine:
    """Adaptateur de visualisation des explications IA (XAI)."""

    @classmethod
    def get_explanation_summary(cls, event_name: str = "Severe Thunderstorm Episode") -> dict[str, Any]:
        """
        NOTE (correction): this used to ignore event_name's content
        (beyond echoing it) and unconditionally claim an identical
        fabricated 5-cause explanation and "91%" confidence for ANY
        event - no real XAI/attribution pipeline is connected here (0
        parameters). Not fabricated.
        """
        return {
            "event": event_name,
            "causes_identified": [],
            "ai_confidence_pct": None,
            "status": "NOT_GENERATED_NO_XAI_PIPELINE_CONNECTED",
            "is_real_data": False,
        }
