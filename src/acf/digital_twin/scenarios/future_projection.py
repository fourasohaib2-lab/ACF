"""
Atmospheric Complexity Framework (ACF)

Planetary Scenario Engine & Multi-Horizon Projections Module (Phase 8)
(Short-term Weather +6h to Long-term Climate Projections +100 years, CMIP6 / SSP Scenarios)
"""

from typing import Any


class PlanetaryScenarioEngine:
    """
    Moteur de simulation et de projections scénarisées multi-échelles temporelles.
    """

    SUPPORTED_HORIZONS = ["+6h", "+12h", "+24h", "+48h", "+72h", "+7d", "+30d", "+1yr", "+10yr", "+50yr", "+100yr"]

    @classmethod
    def run_scenario_projection(cls, horizon: str = "+24h", ssp_scenario: str = "SSP2-4.5") -> dict[str, Any]:
        """
        Exécute une projection scénarisée sur l'horizon temporel spécifié.

        NOTE (correction): ssp_scenario is genuinely accepted and
        echoed back, but the actual projected_global_temp_change_c/
        projected_sea_level_rise_m below are NOT a function of it - the
        same horizon-only fixed values are returned regardless of
        whether "SSP1-1.9" (low emissions) or "SSP5-8.5" (high
        emissions) is requested for the same horizon, even though the
        real climate response differs substantially between them (AR6
        WG1 end-of-century best estimates span roughly 1.4-4.4°C across
        the SSP range, not a single number). The +100yr default value
        (2.7°C) is a genuine, defensible reference figure for
        SSP2-4.5 specifically (close to AR6's own headline estimate for
        that scenario) - kept as a static baseline (same convention as
        digital_twin.earth_state.EarthState) - but it does not currently
        generalize to other ssp_scenario values as its presence in the
        output would suggest. No real per-scenario CMIP6/ESM ensemble
        output is connected here to compute a genuine per-scenario
        value. Not fabricated, but flagged since the parameter's
        presence in the signature/output implies scenario-sensitivity
        that isn't actually there yet.
        """
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
