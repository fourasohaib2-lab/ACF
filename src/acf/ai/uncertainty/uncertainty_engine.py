"""
Atmospheric Complexity Framework (ACF)

Uncertainty Quantification Engine (Aleatoric, Epistemic, Deep Ensembles & Monte Carlo Dropout)
"""

import math
from typing import Dict, List, Optional, Tuple


class UncertaintyQuantificationEngine:
    """
    Moteur de quantification et de propagation de l'incertitude dans les prédictions IA.
    """

    @classmethod
    def decompose_uncertainty(cls, predictions: List[float], aleatoric_variances: Optional[List[float]] = None) -> Dict[str, float]:
        """
        Décompose l'incertitude totale en composante Épistémique (manque de connaissances du modèle)
        et Aléatoire (bruit intrinsèque des observations).
        """
        n = len(predictions)
        if n == 0:
            return {"mean": 0.0, "total_std": 0.0, "epistemic_std": 0.0, "aleatoric_std": 0.0}

        mean_pred = sum(predictions) / n
        epistemic_var = sum((p - mean_pred) ** 2 for p in predictions) / max(1, n - 1)

        if aleatoric_variances and len(aleatoric_variances) == n:
            aleatoric_var = sum(aleatoric_variances) / n
        else:
            aleatoric_var = 0.1 * epistemic_var

        total_var = epistemic_var + aleatoric_var

        return {
            "mean": mean_pred,
            "total_std": math.sqrt(total_var),
            "epistemic_std": math.sqrt(epistemic_var),
            "aleatoric_std": math.sqrt(aleatoric_var),
            "epistemic_fraction": epistemic_var / max(1e-6, total_var),
            "confidence_score": max(0.0, min(1.0, 1.0 - math.sqrt(total_var) / (abs(mean_pred) + 1.0))),
        }

    @classmethod
    def calculate_confidence_interval(cls, mean: float, std: float, confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calcule l'intervalle de confiance à [mean - z*std, mean + z*std]."""
        z = 1.96 if confidence_level == 0.95 else 2.576
        return (mean - z * std, mean + z * std)
