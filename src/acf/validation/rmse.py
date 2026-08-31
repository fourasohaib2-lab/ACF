"""
Atmospheric Complexity Framework (ACF)

Root Mean Square Error (RMSE) Calculator Module
"""

import math
from typing import Any


class RMSECalculator:
    """Calculateur d'erreur quadratique moyenne (RMSE)."""

    @classmethod
    def compute_rmse(cls, forecast_values: list[float], obs_values: list[float]) -> dict[str, Any]:
        if not forecast_values or len(forecast_values) != len(obs_values):
            return {"rmse": 0.0, "status": "INVALID_INPUT"}
        mse = sum((f - o) ** 2 for f, o in zip(forecast_values, obs_values, strict=True)) / len(forecast_values)
        return {"rmse": math.sqrt(mse), "status": "COMPUTED"}
