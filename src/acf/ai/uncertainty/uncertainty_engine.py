"""
Atmospheric Complexity Framework (ACF)

Uncertainty Quantification Engine (Aleatoric, Epistemic, Deep Ensembles & Monte Carlo Dropout)
"""

import math


class UncertaintyQuantificationEngine:
    """
    Moteur de quantification et de propagation de l'incertitude dans les prédictions IA.
    """

    # Two-tailed normal-distribution z-scores for common confidence levels.
    _Z_SCORES: dict[float, float] = {
        0.80: 1.282,
        0.90: 1.645,
        0.95: 1.96,
        0.98: 2.326,
        0.99: 2.576,
    }

    @classmethod
    def decompose_uncertainty(
        cls, predictions: list[float], aleatoric_variances: list[float] | None = None
    ) -> dict[str, float]:
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
    def calculate_confidence_interval(
        cls, mean: float, std: float, confidence_level: float = 0.95
    ) -> tuple[float, float]:
        """
        Calcule l'intervalle de confiance à [mean - z*std, mean + z*std].

        NOTE (correction): this used to be "z = 1.96 if confidence_level
        == 0.95 else 2.576" - any confidence_level other than exactly
        0.95 (e.g. the very reasonable 0.90) silently got z=2.576, the
        z-score for a 99% CI, not the correct one for whatever level was
        actually requested. calculate_confidence_interval(mean, std,
        confidence_level=0.90) returned a 99%-wide interval mislabeled
        as 90%. Now looks up the real z-score for the requested level
        and fails closed (raises) for an unsupported one rather than
        silently substituting the wrong width.
        """
        z = cls._Z_SCORES.get(round(confidence_level, 2))
        if z is None:
            raise ValueError(
                f"Unsupported confidence_level={confidence_level!r}; supported values: "
                f"{sorted(cls._Z_SCORES)}"
            )
        return (mean - z * std, mean + z * std)
