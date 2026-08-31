"""
Atmospheric Complexity Framework (ACF)

Probabilistic Ensemble Visualizer Module
"""

from typing import Any


class EnsembleVisualizer:
    """Visualiseur d'ensembles probabilistes (Plumes, Diagrammes spaghetti, Dispersion)."""

    @classmethod
    def get_ensemble_summary(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim a
        fabricated "50-member IFS EPS + GenCast" ensemble with 0
        parameters and no real ensemble run connected. Not fabricated.
        """
        return {
            "ensemble_members_count": None,
            "ensemble_type": None,
            "spaghetti_lines_count": 0,
            "status": "NOT_RENDERED_NO_ENSEMBLE_RUN_CONNECTED",
            "is_real_data": False,
        }
