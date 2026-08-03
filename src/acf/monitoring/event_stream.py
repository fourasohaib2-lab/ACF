"""
Atmospheric Complexity Framework (ACF)

Planetary Event Stream & Priority Bus Module (Phase 5)
(PlanetaryEventStream for pub/sub messaging and event queue management)
"""

from typing import Any, Callable, Dict, List


EVENT_TYPES = [
    "CycloneDetected", "FloodDetected", "HeatwaveDetected", "WildfireDetected",
    "VolcanoDetected", "EarthquakeDetected", "SolarStormDetected", "TornadoDetected",
    "HailDetected", "FlashFloodDetected", "LightningDetected", "DustStormDetected", "AirPollutionDetected"
]


class PlanetaryEventStream:
    """
    Bus d'événements géophysiques planétaires à priorité distribuée.
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {evt: [] for evt in EVENT_TYPES}
        self.published_events_history: List[Dict[str, Any]] = []

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """S'abonne à un type d'événement planétaire."""
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, payload: Dict[str, Any], priority: str = "HIGH") -> Dict[str, Any]:
        """Publie un événement géophysique sur le bus."""
        record = {"event_type": event_type, "priority": priority, "payload": payload}
        self.published_events_history.append(record)
        return {"status": "PUBLISHED", "event": record}
