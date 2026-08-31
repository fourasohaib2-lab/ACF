"""
Atmospheric Complexity Framework (ACF)

XAI Explanation Generator Engine Module
"""

from typing import Any

from acf.ai.xai.causal_chain import CausalChainGenerator


class XAIExplanationGenerator:
    """Générateur d'explications scientifiques explicables (XAI)."""

    @classmethod
    def generate_explanation(cls, target_event: str = "Severe Thunderstorm Episode") -> dict[str, Any]:
        """
        NOTE (correction): target_event is genuinely echoed, but this
        used to also claim a fabricated "91%" confidence and
        "EXPLANATION_GENERATED_SUCCESS" regardless of target_event -
        CausalChainGenerator (also fixed this session) now honestly
        returns an empty chain, so this correctly propagates that.
        """
        return {
            "target_event": target_event,
            "causal_chain": CausalChainGenerator.generate_causal_chain(),
            "confidence_score_pct": None,
            "status": "NOT_GENERATED_NO_CAUSAL_ATTRIBUTION_PIPELINE_CONNECTED",
            "is_real_data": False,
        }
