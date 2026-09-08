"""
Atmospheric Complexity Framework (ACF)

Forecast Bias Analysis Module
"""

from typing import Any


class BiasAnalysis:
    """Calculateur de biais moyen (Forecast minus Observation)."""

    @classmethod
    def compute_bias(cls, forecast_mean: float, obs_mean: float) -> dict[str, Any]:
        bias = forecast_mean - obs_mean
        return {
            "bias_value": bias,
            "bias_status": "NEUTRAL" if abs(bias) < 0.1 else "POSITIVE" if bias > 0 else "NEGATIVE",
        }
