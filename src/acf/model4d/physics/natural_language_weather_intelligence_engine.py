from dataclasses import dataclass


@dataclass(slots=True)
class NaturalLanguageWeatherState:
    region: str
    dominant_weather: str
    hazard_probability: float
    confidence: float
    models_agreement: float
    temperature_trend: str
    precipitation_signal: str


class NaturalLanguageWeatherIntelligenceEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.48
    Natural Language Weather Intelligence Engine

    Converts numerical weather prediction outputs
    into meteorological explanations.
    """

    def hazard_level(
        self,
        state: NaturalLanguageWeatherState,
    ) -> str:
        """
        Classify hazard probability.
        """

        if state.hazard_probability >= 80:
            return "EXTREME"

        if state.hazard_probability >= 60:
            return "HIGH"

        if state.hazard_probability >= 30:
            return "MODERATE"

        return "LOW"



    def confidence_level(
        self,
        state: NaturalLanguageWeatherState,
    ) -> str:
        """
        Forecast confidence classification.
        """

        if state.confidence >= 80:
            return "HIGH"

        if state.confidence >= 60:
            return "MEDIUM"

        return "LOW"



    def model_interpretation(
        self,
        state: NaturalLanguageWeatherState,
    ) -> str:
        """
        Explain model agreement.
        """

        if state.models_agreement >= 80:
            return (
                "Les modèles numériques présentent "
                "une forte convergence."
            )

        if state.models_agreement >= 50:
            return (
                "Les modèles montrent un scénario "
                "globalement cohérent avec quelques incertitudes."
            )

        return (
            "Les modèles divergent fortement, "
            "la prévision reste incertaine."
        )



    def generate_weather_explanation(
        self,
        state: NaturalLanguageWeatherState,
    ) -> str:
        """
        Generate human meteorological explanation.
        """

        hazard = self.hazard_level(state)
        confidence = self.confidence_level(state)
        agreement = self.model_interpretation(state)

        return (
            f"Pour la région {state.region}, "
            f"la situation dominante est {state.dominant_weather}. "
            f"{agreement} "
            f"La probabilité d'un phénomène significatif "
            f"est classée {hazard}. "
            f"La confiance de la prévision est {confidence}. "
            f"La tendance thermique indique {state.temperature_trend}. "
            f"Le signal précipitation est {state.precipitation_signal}."
        )



    def bulletin_summary(
        self,
        state: NaturalLanguageWeatherState,
    ) -> dict:
        """
        Generate complete weather intelligence report.
        """

        return {
            "region": state.region,
            "hazard_level": self.hazard_level(state),
            "confidence_level": self.confidence_level(state),
            "model_interpretation":
                self.model_interpretation(state),
            "explanation":
                self.generate_weather_explanation(state),
        }
