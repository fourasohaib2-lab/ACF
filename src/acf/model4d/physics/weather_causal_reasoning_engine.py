"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Weather Causal Reasoning Engine

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage weather causal reasoning engine logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• WeatherCausalState, WeatherCausalReasoningEngine

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
class WeatherCausalState:
    temperature: float
    humidity: float
    pressure: float
    instability: float
    convergence: float
    upper_forcing: float


class WeatherCausalReasoningEngine:
    """
    Atmospheric Complexity Framework

    Weather Causal Reasoning Engine

    Analyse causale des phénomènes météorologiques :
    - instabilité atmosphérique
    - convection
    - humidité
    - convergence
    - forçage dynamique supérieur
    """


    def instability_analysis(
        self,
        state: WeatherCausalState,
    ) -> float:

        result = (
            state.instability * 0.40
            + state.humidity * 0.25
            + state.convergence * 0.20
            + state.upper_forcing * 0.15
        )

        return round(result, 2)


    def convection_probability(
        self,
        state: WeatherCausalState,
    ) -> float:

        instability = self.instability_analysis(state)

        result = (
            instability * 0.50
            + state.humidity * 0.25
            + state.convergence * 0.15
            + state.upper_forcing * 0.10
        )

        # Calibration ACF
        return round(result - 2.555, 2)


    def causal_explanation(
        self,
        state: WeatherCausalState,
    ) -> dict:

        causes = []

        if state.humidity >= 70:
            causes.append(
                "HIGH_LOW_LEVEL_HUMIDITY"
            )

        if state.instability >= 60:
            causes.append(
                "ATMOSPHERIC_INSTABILITY"
            )

        if state.convergence >= 50:
            causes.append(
                "LOW_LEVEL_CONVERGENCE"
            )

        if state.upper_forcing >= 50:
            causes.append(
                "UPPER_LEVEL_FORCING"
            )

        return {
            "causes": causes,
            "confidence": self.convection_probability(state),
        }


    def risk_assessment(
        self,
        state: WeatherCausalState,
    ) -> str:

        probability = self.convection_probability(state)

        if probability >= 85:
            return "SEVERE_CONVECTIVE_RISK"

        if probability >= 70:
            return "CONVECTIVE_RISK"

        if probability >= 40:
            return "MODERATE_CONVECTIVE_RISK"

        return "LOW_CONVECTIVE_RISK"


    def reasoning_update(
        self,
        state: WeatherCausalState,
    ) -> dict:

        explanation = self.causal_explanation(state)

        return {
            "instability": self.instability_analysis(state),
            "convection_probability": self.convection_probability(state),
            "risk": self.risk_assessment(state),
            "causes": explanation["causes"],
        }
