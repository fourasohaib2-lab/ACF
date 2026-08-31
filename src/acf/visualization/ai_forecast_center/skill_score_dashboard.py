"""
Atmospheric Complexity Framework (ACF)

Forecast Skill & Verification Dashboard Module (Phase 11)
"""

from typing import Any


class SkillScoreDashboard:
    """Tableau de bord d'évaluation de la performance des prévisions (Skill Scores)."""

    @classmethod
    def get_skill_metrics(cls, model_name: str = "GraphCast") -> dict[str, Any]:
        """
        NOTE (correction): this used to ignore model_name's content
        (beyond echoing it) and unconditionally claim an identical
        fabricated skill-score battery (RMSE/MAE/Bias/ACC/Brier/ROC/
        CRPS) and "OUTPERFORMS_OPERATIONAL_BASELINE" for ANY model, as
        if a real forecast-verification run had been performed - none
        was (0 real forecast/observation pairs connected). A false
        performance claim in a verification dashboard could mislead an
        operational decision about which model to trust. Not
        fabricated.
        """
        return {
            "model_evaluated": model_name,
            "deterministic_metrics": {},
            "probabilistic_metrics": {},
            "evaluation": "NOT_EVALUATED_NO_VERIFICATION_DATA_CONNECTED",
            "is_real_data": False,
        }
