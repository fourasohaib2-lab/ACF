"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Hybrid Forecast Fusion Engine

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage hybrid forecast fusion engine logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• HybridForecastFusionState, HybridForecastFusionEngine

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.model4d module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(slots=True)
class HybridForecastFusionState:
    """
    Multi-model forecast inputs.

    All model scores are normalized between 0 and 100.
    """

    arpege: float
    arome: float
    wrf: float
    icon: float
    ecmwf: float

    arpege_quality: float
    arome_quality: float
    wrf_quality: float
    icon_quality: float
    ecmwf_quality: float

    atmosphere_stability: float
    observation_quality: float
    forecast_consistency: float


class HybridForecastFusionEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.43

    Hybrid Forecast Fusion Engine

    Objective
    ---------
    Produce a unique Model4D forecast from multiple NWP models.
    """

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, value))

    # ============================================================
    # Dynamic weights
    # ============================================================

    def arpege_weight(self, state: HybridForecastFusionState) -> float:
        return round(
            self._clamp(
                state.arpege_quality * 0.55
                + state.observation_quality * 0.25
                + state.forecast_consistency * 0.20
            ),
            2,
        )

    def arome_weight(self, state: HybridForecastFusionState) -> float:
        return round(
            self._clamp(
                state.arome_quality * 0.60
                + state.observation_quality * 0.25
                + state.atmosphere_stability * 0.15
            ),
            2,
        )

    def wrf_weight(self, state: HybridForecastFusionState) -> float:
        return round(
            self._clamp(
                state.wrf_quality * 0.55
                + state.forecast_consistency * 0.25
                + state.atmosphere_stability * 0.20
            ),
            2,
        )

    def icon_weight(self, state: HybridForecastFusionState) -> float:
        return round(
            self._clamp(
                state.icon_quality * 0.60
                + state.forecast_consistency * 0.20
                + state.observation_quality * 0.20
            ),
            2,
        )

    def ecmwf_weight(self, state: HybridForecastFusionState) -> float:
        return round(
            self._clamp(
                state.ecmwf_quality * 0.65
                + state.forecast_consistency * 0.20
                + state.observation_quality * 0.15
            ),
            2,
        )

    # ============================================================
    # Model scores
    # ============================================================

    def arpege_score(self, state: HybridForecastFusionState) -> float:
        return round(
            state.arpege * self.arpege_weight(state) / 100.0,
            2,
        )

    def arome_score(self, state: HybridForecastFusionState) -> float:
        return round(
            state.arome * self.arome_weight(state) / 100.0,
            2,
        )

    def wrf_score(self, state: HybridForecastFusionState) -> float:
        return round(
            state.wrf * self.wrf_weight(state) / 100.0,
            2,
        )

    def icon_score(self, state: HybridForecastFusionState) -> float:
        return round(
            state.icon * self.icon_weight(state) / 100.0,
            2,
        )

    def ecmwf_score(self, state: HybridForecastFusionState) -> float:
        return round(
            state.ecmwf * self.ecmwf_weight(state) / 100.0,
            2,
        )

    # ============================================================
    # Global diagnostics
    # ============================================================

    def average_weight(self, state: HybridForecastFusionState) -> float:
        return round(
            mean(
                [
                    self.arpege_weight(state),
                    self.arome_weight(state),
                    self.wrf_weight(state),
                    self.icon_weight(state),
                    self.ecmwf_weight(state),
                ]
            ),
            2,
        )

    def average_model_score(self, state: HybridForecastFusionState) -> float:
        return round(
            mean(
                [
                    self.arpege_score(state),
                    self.arome_score(state),
                    self.wrf_score(state),
                    self.icon_score(state),
                    self.ecmwf_score(state),
                ]
            ),
            2,
        )

    # ============================================================
    # Forecast spread
    # ============================================================

    def forecast_spread(
        self,
        state: HybridForecastFusionState,
    ) -> float:
        values = [
            state.arpege,
            state.arome,
            state.wrf,
            state.icon,
            state.ecmwf,
        ]

        return round(max(values) - min(values), 2)

    # ============================================================
    # Confidence
    # ============================================================

    def confidence_score(
        self,
        state: HybridForecastFusionState,
    ) -> float:

        spread_penalty = self.forecast_spread(state) * 0.30

        confidence = (
            self.average_weight(state)
            + state.forecast_consistency * 0.35
            + state.observation_quality * 0.25
            - spread_penalty
        )

        return round(self._clamp(confidence), 2)

    # ============================================================
    # Hybrid forecast
    # ============================================================

    def hybrid_forecast(
        self,
        state: HybridForecastFusionState,
    ) -> float:

        scores = [
            self.arpege_score(state),
            self.arome_score(state),
            self.wrf_score(state),
            self.icon_score(state),
            self.ecmwf_score(state),
        ]

        return round(mean(scores), 2)

    # ============================================================
    # Fusion index
    # ============================================================

    def fusion_index(
        self,
        state: HybridForecastFusionState,
    ) -> float:

        value = (
            self.hybrid_forecast(state)
            + self.confidence_score(state)
            + self.average_model_score(state)
        ) / 3

        return round(value, 2)

    # ============================================================
    # Best model
    # ============================================================

    def best_model(
        self,
        state: HybridForecastFusionState,
    ) -> str:

        scores = {
            "ARPEGE": self.arpege_score(state),
            "AROME": self.arome_score(state),
            "WRF": self.wrf_score(state),
            "ICON": self.icon_score(state),
            "ECMWF": self.ecmwf_score(state),
        }

        return max(scores, key=scores.get)

    # ============================================================
    # Model4D readiness
    # ============================================================

    def model4d_ready(
        self,
        state: HybridForecastFusionState,
    ) -> bool:

        return (
            self.hybrid_forecast(state) >= 40.0
            and self.confidence_score(state) >= 60.0
            and self.average_weight(state) >= 50.0
        )

    # ============================================================
    # Export
    # ============================================================

    def fusion_update(
        self,
        state: HybridForecastFusionState,
    ) -> dict:

        return {
            "arpege_weight": self.arpege_weight(state),
            "arome_weight": self.arome_weight(state),
            "wrf_weight": self.wrf_weight(state),
            "icon_weight": self.icon_weight(state),
            "ecmwf_weight": self.ecmwf_weight(state),
            "average_weight": self.average_weight(state),
            "arpege_score": self.arpege_score(state),
            "arome_score": self.arome_score(state),
            "wrf_score": self.wrf_score(state),
            "icon_score": self.icon_score(state),
            "ecmwf_score": self.ecmwf_score(state),
            "average_model_score": self.average_model_score(state),
            "forecast_spread": self.forecast_spread(state),
            "confidence_score": self.confidence_score(state),
            "hybrid_forecast": self.hybrid_forecast(state),
            "fusion_index": self.fusion_index(state),
            "best_model": self.best_model(state),
            "model4d_ready": self.model4d_ready(state),
        }
