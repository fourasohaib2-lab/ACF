from dataclasses import dataclass


@dataclass(slots=True)
class WeatherIntelligenceInput:
    region: str
    models: list
    observation_score: float
    ensemble_score: float
    hazard_probability: float
    confidence: float
    uncertainty: float
    weather_description: str


class WeatherIntelligenceOrchestrator:
    """
    Atmospheric Complexity Framework

    Sprint 9.50
    Weather Intelligence Orchestrator

    Central coordination layer of Model4D.
    """

    def active_models(
        self,
        data: WeatherIntelligenceInput,
    ) -> int:
        return len(data.models)



    def observation_quality(
        self,
        data: WeatherIntelligenceInput,
    ) -> float:
        return round(
            data.observation_score,
            2,
        )



    def ensemble_quality(
        self,
        data: WeatherIntelligenceInput,
    ) -> float:
        return round(
            data.ensemble_score,
            2,
        )



    def risk_level(
        self,
        data: WeatherIntelligenceInput,
    ) -> str:

        if data.hazard_probability >= 80:
            return "EXTREME"

        if data.hazard_probability >= 60:
            return "HIGH"

        if data.hazard_probability >= 30:
            return "MODERATE"

        return "LOW"



    def forecast_confidence(
        self,
        data: WeatherIntelligenceInput,
    ) -> float:

        value = (
            data.confidence
            + data.observation_score
            + data.ensemble_score
            - data.uncertainty
        ) / 3

        return round(
            max(min(value, 100), 0),
            2,
        )



    def operational_decision(
        self,
        data: WeatherIntelligenceInput,
    ) -> str:

        risk = self.risk_level(data)
        confidence = self.forecast_confidence(data)

        if risk == "EXTREME" and confidence >= 75:
            return "EMERGENCY_RESPONSE"

        if risk == "HIGH" and confidence >= 60:
            return "WEATHER_WARNING"

        if risk == "MODERATE":
            return "INCREASE_MONITORING"

        return "NORMAL_OPERATION"



    def generate_intelligence_report(
        self,
        data: WeatherIntelligenceInput,
    ) -> dict:

        return {

            "region":
                data.region,

            "models_used":
                self.active_models(data),

            "observation_quality":
                self.observation_quality(data),

            "ensemble_quality":
                self.ensemble_quality(data),

            "risk_level":
                self.risk_level(data),

            "confidence":
                self.forecast_confidence(data),

            "decision":
                self.operational_decision(data),

            "description":
                data.weather_description,
        }
