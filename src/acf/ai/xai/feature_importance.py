"""
Atmospheric Complexity Framework (ACF)

SHAP / Integrated Gradients Feature Importance Module
"""

from typing import Any


class FeatureImportanceAnalyzer:
    """Calculateur d'importance des variables d'entrée (SHAP / Integrated Gradients)."""

    @classmethod
    def compute_feature_importance(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim 3
        fabricated SHAP-style feature-importance scores with 0
        parameters and no real model/input-data connected - no SHAP
        or Integrated Gradients computation actually ran. Not
        fabricated.
        """
        return {
            "top_features": [],
            "status": "NOT_COMPUTED_NO_MODEL_INPUT_DATA_CONNECTED",
            "is_real_data": False,
        }
