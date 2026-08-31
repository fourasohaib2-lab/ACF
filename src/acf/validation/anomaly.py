"""
Atmospheric Complexity Framework (ACF)

Scientific Anomaly & Anomaly Correlation (ACC) Module
"""

from typing import Any


class AnomalyCalculator:
    """Calculateur d'anomalies climatologiques et de coefficient de corrélation (ACC)."""

    @classmethod
    def compute_anomaly(cls, val: float, climatology_val: float) -> dict[str, Any]:
        return {"anomaly": val - climatology_val, "standardized_anomaly_sigma": (val - climatology_val) / 1.5}
