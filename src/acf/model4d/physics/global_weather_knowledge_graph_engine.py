from dataclasses import dataclass


@dataclass(slots=True)
class WeatherKnowledgeNode:
    event_id: str
    location: str
    phenomenon: str
    intensity: float
    temperature: float
    pressure: float
    humidity: float
    impact_level: float


class GlobalWeatherKnowledgeGraphEngine:
    """
    Atmospheric Complexity Framework

    Sprint 9.53
    Global Weather Knowledge Graph Engine

    Meteorological memory and analogue discovery layer.
    """

    def create_weather_signature(
        self,
        node: WeatherKnowledgeNode,
    ) -> dict:
        """
        Create atmospheric event signature.
        """

        return {
            "event_id": node.event_id,
            "location": node.location,
            "phenomenon": node.phenomenon,
            "signature": round(
                (
                    node.intensity
                    + node.temperature
                    + node.pressure
                    + node.humidity
                ) / 4,
                2,
            ),
        }



    def risk_classification(
        self,
        node: WeatherKnowledgeNode,
    ) -> str:
        """
        Classify weather impact.
        """

        if node.impact_level >= 80:
            return "EXTREME_EVENT"

        if node.impact_level >= 50:
            return "SIGNIFICANT_EVENT"

        return "NORMAL_EVENT"



    def atmospheric_similarity(
        self,
        first: WeatherKnowledgeNode,
        second: WeatherKnowledgeNode,
    ) -> float:
        """
        Compare two atmospheric situations.
        """

        difference = (
            abs(first.intensity - second.intensity)
            + abs(first.temperature - second.temperature)
            + abs(first.pressure - second.pressure)
            + abs(first.humidity - second.humidity)
        )

        similarity = 100 - difference / 4

        return round(
            max(min(similarity, 100), 0),
            2,
        )



    def find_weather_analogue(
        self,
        current: WeatherKnowledgeNode,
        historical: list,
    ) -> dict:
        """
        Search closest historical event.
        """

        best_event = None
        best_score = -1

        for event in historical:

            score = self.atmospheric_similarity(
                current,
                event,
            )

            if score > best_score:
                best_score = score
                best_event = event


        return {
            "analogue_event":
                best_event.event_id
                if best_event
                else None,

            "similarity":
                round(best_score, 2),
        }



    def knowledge_update(
        self,
        node: WeatherKnowledgeNode,
    ) -> dict:
        """
        Store weather intelligence information.
        """

        return {
            "signature":
                self.create_weather_signature(node),

            "risk":
                self.risk_classification(node),
        }
