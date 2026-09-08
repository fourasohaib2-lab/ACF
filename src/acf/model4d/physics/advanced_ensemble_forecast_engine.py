"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Advanced Ensemble Forecast Engine

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage advanced ensemble forecast engine logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• AdvancedEnsembleForecastState, AdvancedEnsembleForecastEngine

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.model4d module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AdvancedEnsembleForecastState:
    arpege: float
    arome: float
    wrf: float
    icon: float
    ecmwf: float

    model_agreement: float
    observation_support: float
    atmospheric_predictability: float


class AdvancedEnsembleForecastEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.44
    Advanced Ensemble Forecast Engine

    Ensemble probabilistic forecasting layer.
    """

    def ensemble_mean(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> float:

        return round(
            (state.arpege + state.arome + state.wrf + state.icon + state.ecmwf) / 5,
            2,
        )

    def ensemble_spread(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> float:

        mean = self.ensemble_mean(state)

        spread = (
            abs(state.arpege - mean)
            + abs(state.arome - mean)
            + abs(state.wrf - mean)
            + abs(state.icon - mean)
            + abs(state.ecmwf - mean)
        ) / 5

        return round(spread, 2)

    def uncertainty_index(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> float:

        return round(
            self.ensemble_spread(state) * 0.75,
            2,
        )

    def confidence_score(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> float:

        score = (state.model_agreement + state.observation_support + state.atmospheric_predictability) / 3

        return round(score, 2)

    def probabilistic_forecast_index(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> float:

        result = (self.ensemble_mean(state) * self.confidence_score(state)) / 100

        return round(result, 2)

    def best_model(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> str:

        models = {
            "ARPEGE": state.arpege,
            "AROME": state.arome,
            "WRF": state.wrf,
            "ICON": state.icon,
            "ECMWF": state.ecmwf,
        }

        return max(
            models,
            key=lambda k: models[k],
        )

    def model4d_ready(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> bool:

        return self.confidence_score(state) >= 70 and self.uncertainty_index(state) <= 15

    def ensemble_update(
        self,
        state: AdvancedEnsembleForecastState,
    ) -> dict:

        return {
            "ensemble_mean": self.ensemble_mean(state),
            "spread": self.ensemble_spread(state),
            "uncertainty": self.uncertainty_index(state),
            "confidence": self.confidence_score(state),
            "probabilistic_index": self.probabilistic_forecast_index(state),
            "best_model": self.best_model(state),
            "model4d_ready": self.model4d_ready(state),
        }
