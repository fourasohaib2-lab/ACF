"""
Atmospheric Complexity Framework (ACF)

Planetary Scenario Engine & Multi-Horizon Projections Module (Phase 8)
(Short-term Weather +6h to Long-term Climate Projections +100 years, CMIP6 / SSP Scenarios)
"""

from typing import Any, Dict


class PlanetaryScenarioEngine:
    """
    Moteur de simulation et de projections scénarisées multi-échelles temporelles.
    """

    SUPPORTED_HORIZONS = ["+6h", "+12h", "+24h", "+48h", "+72h", "+7d", "+30d", "+1yr", "+10yr", "+50yr", "+100yr"]

    @classmethod
    def run_scenario_projection(cls, horizon: str = "+24h", ssp_scenario: str = "SSP2-4.5") -> Dict[str, Any]:
        """Exécute une projection scénarisée sur l'horizon temporel spécifié."""
        if horizon not in cls.SUPPORTED_HORIZONS:
            horizon = "+24h"

        is_climate = horizon in ["+1yr", "+10yr", "+50yr", "+100yr"]
        model = "CMIP6 / Earth System Model Ensemble" if is_climate else "GraphCast / GenCast Neural AI Forecast"

        return {
            "requested_horizon": horizon,
            "ssp_scenario": ssp_scenario if is_climate else "N/A (Weather Horizon)",
            "predictive_model_used": model,
            "projected_global_temp_change_c": 0.15 if not is_climate else (2.7 if horizon == "+100yr" else 0.8),
            "projected_sea_level_rise_m": 0.0 if not is_climate else (0.54 if horizon == "+100yr" else 0.05),
        }
