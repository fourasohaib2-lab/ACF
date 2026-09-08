"""
Atmospheric Complexity Framework (ACF)

Climate Verification & Statistical Metrics Module
(Anomalies, Trends, ACC Anomaly Correlation Coefficient, RMSE, Bias, Taylor Diagram Metadata)
"""

import math
from typing import Any


class ClimateVerificationEngine:
    """
    Moteur d'évaluation statistique des biais, tendances décennales et performances des modèles climatiques.
    """

    @staticmethod
    def calculate_anomaly(value: float, climatological_mean: float) -> float:
        """Calcule l'anomalie d'une valeur par rapport à sa normale climatologique (30 ans)."""
        return value - climatological_mean

    @staticmethod
    def anomaly_correlation_coefficient(forecast_anomalies: list[float], observed_anomalies: list[float]) -> float:
        """Calcule le coefficient de corrélation d'anomalie ACC (Anomaly Correlation Coefficient)."""
        if len(forecast_anomalies) != len(observed_anomalies) or not forecast_anomalies:
            return 0.0
        n = len(forecast_anomalies)
        mean_f = sum(forecast_anomalies) / n
        mean_o = sum(observed_anomalies) / n

        num = sum((f - mean_f) * (o - mean_o) for f, o in zip(forecast_anomalies, observed_anomalies, strict=True))
        den_f = math.sqrt(sum((f - mean_f) ** 2 for f in forecast_anomalies))
        den_o = math.sqrt(sum((o - mean_o) ** 2 for o in observed_anomalies))

        if den_f == 0.0 or den_o == 0.0:
            return 0.0
        return num / (den_f * den_o)

    @staticmethod
    def calculate_decadal_trend(values_annual: list[float]) -> float:
        """Calcule la tendance linéaire par décennie (°C / décennie)."""
        n = len(values_annual)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2.0
        y_mean = sum(values_annual) / n

        num = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(values_annual))
        den = sum((i - x_mean) ** 2 for i in range(n))

        if den == 0.0:
            return 0.0
        annual_slope = num / den
        return annual_slope * 10.0  # Tendance sur 10 ans

    @classmethod
    def taylor_diagram_metadata(cls, forecast: list[float], reference: list[float]) -> dict[str, Any]:
        """Génère les métadonnées pour le tracé d'un diagramme de Taylor (Corrélation, RMSE, Écart-type relatif)."""
        n = len(forecast)
        if n == 0 or len(reference) != n:
            return {"correlation": 0.0, "std_forecast": 0.0, "std_reference": 0.0, "crmse": 0.0}

        mean_f = sum(forecast) / n
        mean_r = sum(reference) / n

        var_f = sum((f - mean_f) ** 2 for f in forecast) / n
        var_r = sum((r - mean_r) ** 2 for r in reference) / n

        std_f = math.sqrt(var_f)
        std_r = math.sqrt(var_r)

        acc = cls.anomaly_correlation_coefficient([f - mean_f for f in forecast], [r - mean_r for r in reference])
        crmse = math.sqrt(sum(((f - mean_f) - (r - mean_r)) ** 2 for f, r in zip(forecast, reference, strict=True)) / n)

        return {
            "correlation": acc,
            "std_forecast": std_f,
            "std_reference": std_r,
            "centered_rmse": crmse,
            "bias": mean_f - mean_r,
        }
