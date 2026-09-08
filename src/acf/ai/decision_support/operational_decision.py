"""
Atmospheric Complexity Framework (ACF)

Operational Decision Support Engine Module (Phase 10)
"""

from typing import Any

from acf.ai.decision_support.decision_engine import ForecastDecisionEngine


class OperationalDecisionSupportEngine:
    """
    Moteur de décision fusionnant l'IA, le Graphe de Connaissances, la Physique, les Radar/Satellite et le NWP.
    """

    def __init__(self):
        self.base_engine = ForecastDecisionEngine()

    def evaluate_operational_situation(
        self,
        nwp_data: dict[str, Any],
        ai_predictions: dict[str, Any],
        radar_summary: dict[str, Any],
        obs_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Évalue la situation opérationnelle globale et génère le consensus des modèles.

        NOTE (correction): ai_predictions, radar_summary and obs_data
        used to be accepted but completely ignored, while
        model_consensus and supporting_observations were fabricated
        fixed text ("IFS vs GraphCast Agreement: High (92%)",
        "Radiosondage 12Z: CAPE mesure = 2100 J/kg", a literal fake
        METAR string) presented as if they were real cross-model
        agreement scores and real observational evidence, regardless
        of the actual (possibly empty) inputs. This is operationally
        risky in a way distinct from a wrong formula: a forecaster
        reading fabricated "supporting observations" could reasonably
        take them as real evidence backing the risk assessment.

        Now: nwp_data still drives the real threshold-based risk
        assessment (base_engine.assess_severe_weather_risk(), which
        was already real). ai_predictions/radar_summary/obs_data are
        genuinely used when they contain data, and the response
        honestly reports when they don't, instead of fabricating
        content to fill the gap.

        FURTHER CORRECTED (this pass): the fallback defaults used for
        any nwp_data field NOT provided by the caller (shear_0_6km=18.0,
        EHI=1.2, IVT=550.0, wind_gust_ms=28.0, CAPE=2000.0) were all
        individually ABOVE assess_severe_weather_risk()'s own detection
        thresholds (shear>=15, EHI>=1.0, IVT>=500, wind_gust>=25,
        CAPE>=1500) - meaning a caller supplying ONLY {"CAPE": 2200.0}
        (genuinely real CAPE, everything else unknown) got FOUR
        fabricated severe-weather alerts (hail, tornado, derecho, flash
        flood) generated purely from the convenient unprovided-field
        defaults, not from any real shear/EHI/wind/IVT data. Now
        defaults to 0.0 (a genuine "no signal" baseline, matching
        assess_severe_weather_risk()'s own internal .get(key, 0.0)
        convention) so a field the caller never supplied cannot
        silently manufacture a risk detection.
        """
        state = {
            "CAPE": nwp_data.get("CAPE", 0.0),
            "shear_0_6km": nwp_data.get("shear_0_6km", 0.0),
            "EHI": nwp_data.get("EHI", 0.0),
            "IVT": nwp_data.get("IVT", 0.0),
            "wind_gust_ms": nwp_data.get("wind_gust_ms", 0.0),
        }

        assessment = self.base_engine.assess_severe_weather_risk(state)

        model_consensus = (
            {k: v for k, v in ai_predictions.items()} if ai_predictions else {"status": "NO_AI_PREDICTIONS_PROVIDED"}
        )

        supporting_observations: list[str] = []
        if obs_data:
            supporting_observations.extend(f"{k}: {v}" for k, v in obs_data.items())
        if radar_summary:
            supporting_observations.extend(f"radar.{k}: {v}" for k, v in radar_summary.items())
        if not supporting_observations:
            supporting_observations = ["NO_OBSERVATIONS_PROVIDED"]

        return {
            "overall_risk_level": assessment["risk_level"],
            "model_consensus": model_consensus,
            "supporting_observations": supporting_observations,
            "explanation": assessment["physical_explanation"],
            "recommended_alerts": assessment["operational_warnings"],
        }
