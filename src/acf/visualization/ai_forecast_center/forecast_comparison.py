"""
Atmospheric Complexity Framework (ACF)

AI Forecast Comparison Matrix Module (Phase 4)
"""

from typing import Any


class ForecastComparisonMatrix:
    """Matrice de comparaison directe des prévisions NWP et IA."""

    @classmethod
    def get_comparison_matrix(cls) -> dict[str, Any]:
        """
        NOTE (correction): parameters/models_evaluated are a genuine
        static declared scope (the intended comparison targets), but
        this used to also claim a fabricated "94.8%" agreement score
        and "READY" with no real multi-model comparison ever run (0
        parameters). Not fabricated.
        """
        return {
            "parameters": ["Temperature", "Precipitation", "Wind", "Storm Risk"],
            "models_evaluated": ["ECMWF IFS", "ICON", "GraphCast", "AIFS", "ACF Ensemble"],
            "matrix_agreement_score_pct": None,
            "status": "NOT_COMPUTED_NO_MODEL_COMPARISON_RUN",
            "is_real_data": False,
        }
