from dataclasses import dataclass


@dataclass(slots=True)
class ExtremeWeatherIntelligenceState:
    ensemble_mean: float
    uncertainty: float
    confidence: float

    temperature_anomaly: float
    precipitation_anomaly: float
    wind_anomaly: float
    convection_index: float


class ProbabilisticExtremeWeatherIntelligenceEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.45
    Probabilistic Extreme Weather Intelligence Engine

    AI-oriented extreme weather risk assessment layer.
    """


    def hazard_probability(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> float:

        risk = (
            state.temperature_anomaly
            + state.precipitation_anomaly
            + state.wind_anomaly
            + state.convection_index
        ) / 4

        return round(
            min(max(risk, 0), 100),
            2,
        )


    def uncertainty_penalty(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> float:

        return round(
            state.uncertainty * 0.35,
            2,
        )


    def corrected_hazard_index(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> float:

        result = (
            self.hazard_probability(state)
            - self.uncertainty_penalty(state)
        )

        return round(
            max(result, 0),
            2,
        )


    def risk_level(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> str:

        index = self.corrected_hazard_index(state)

        if index >= 80:
            return "EXTREME"

        if index >= 60:
            return "HIGH"

        if index >= 40:
            return "MODERATE"

        return "LOW"


    def alert_level(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> int:

        index = self.corrected_hazard_index(state)

        if index >= 80:
            return 4

        if index >= 60:
            return 3

        if index >= 40:
            return 2

        return 1


    def model4d_ready(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> bool:

        return (
            state.confidence >= 70
            and self.corrected_hazard_index(state) >= 40
        )


    def intelligence_update(
        self,
        state: ExtremeWeatherIntelligenceState,
    ) -> dict:

        return {
            "hazard_probability":
                self.hazard_probability(state),

            "uncertainty_penalty":
                self.uncertainty_penalty(state),

            "hazard_index":
                self.corrected_hazard_index(state),

            "risk_level":
                self.risk_level(state),

            "alert_level":
                self.alert_level(state),

            "model4d_ready":
                self.model4d_ready(state),
        }
