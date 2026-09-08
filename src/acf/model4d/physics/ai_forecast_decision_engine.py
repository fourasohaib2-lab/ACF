"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Ai Forecast Decision Engine

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage ai forecast decision engine logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• AIForecastDecisionState, AIForecastDecisionEngine

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
class AIForecastDecisionState:
    hazard_index: float
    confidence: float
    forecast_quality: float
    observation_quality: float
    uncertainty: float


class AIForecastDecisionEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.46
    AI Forecast Decision Engine

    AI operational decision layer for Model4D.
    """

    def decision_score(
        self,
        state: AIForecastDecisionState,
    ) -> float:
        """
        Compute global AI forecast decision score.

        NOTE (correction - Physics Guard, operationally relevant): the
        weighted sum above (0.55/0.15/0.10/0.10/-0.05 weights) is a
        genuine, documented heuristic, but it used to be followed by an
        unexplained "- 0.75" with no comment or justification anywhere
        - the same unexplained-offset pattern already found and removed
        in AdaptiveForecastControlEngine/ForecastConfidenceCalibrationEngine
        elsewhere in model4d/physics/ this session. This score directly
        drives recommended_action()/priority_level() (hazard-alert
        escalation), so an arbitrary offset here could shift an
        operational alert decision near a threshold with no physical
        basis. For this class's own reference test state it happened
        not to cross a threshold (77.0 fudged vs 77.75 honest, both in
        the same 70-90 "ISSUE_WEATHER_WARNING" bracket), but that is
        incidental, not a guarantee for other inputs. Removed.
        """

        score = (
            state.hazard_index * 0.55
            + state.confidence * 0.15
            + state.forecast_quality * 0.10
            + state.observation_quality * 0.10
            - state.uncertainty * 0.05
        )

        return round(
            max(min(score, 100.0), 0.0),
            2,
        )

    def confidence_level(
        self,
        state: AIForecastDecisionState,
    ) -> str:
        """
        Classify forecast confidence.
        """

        if state.confidence >= 85:
            return "VERY_HIGH"

        if state.confidence >= 70:
            return "HIGH"

        if state.confidence >= 50:
            return "MEDIUM"

        return "LOW"

    def recommended_action(
        self,
        state: AIForecastDecisionState,
    ) -> str:
        """
        Determine recommended meteorological action.
        """

        score = self.decision_score(state)

        if score >= 90:
            return "ACTIVATE_MAXIMUM_ALERT"

        if score >= 70:
            return "ISSUE_WEATHER_WARNING"

        if state.hazard_index < 30:
            return "NORMAL_OPERATION"

        return "INCREASE_MONITORING"

    def priority_level(
        self,
        state: AIForecastDecisionState,
    ) -> int:
        """
        Priority scale:

        1 -> Normal operation
        2 -> Monitoring
        3 -> Warning
        4 -> Emergency
        """

        score = self.decision_score(state)

        if score >= 90:
            return 4

        if score >= 70:
            return 3

        if state.hazard_index < 30:
            return 1

        return 2

    def automatic_response(
        self,
        state: AIForecastDecisionState,
    ) -> str:
        """
        Generate automatic operational message.
        """

        action = self.recommended_action(state)

        response_map = {
            "ACTIVATE_MAXIMUM_ALERT": "Immediate emergency meteorological response required",
            "ISSUE_WEATHER_WARNING": "Issue official weather warning",
            "INCREASE_MONITORING": "Increase forecast monitoring frequency",
            "NORMAL_OPERATION": "Continue standard forecasting workflow",
        }

        return response_map[action]

    def model4d_ready(
        self,
        state: AIForecastDecisionState,
    ) -> bool:
        """
        Validate Model4D operational readiness.
        """

        return state.confidence >= 70 and state.forecast_quality >= 70 and state.observation_quality >= 70

    def decision_update(
        self,
        state: AIForecastDecisionState,
    ) -> dict:
        """
        Complete AI decision report.
        """

        return {
            "decision_score": self.decision_score(state),
            "confidence_level": self.confidence_level(state),
            "recommended_action": self.recommended_action(state),
            "priority_level": self.priority_level(state),
            "automatic_response": self.automatic_response(state),
            "model4d_ready": self.model4d_ready(state),
        }
