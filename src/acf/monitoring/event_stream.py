"""
Atmospheric Complexity Framework (ACF)

Planetary Event Stream & Priority Bus Module (Phase 5)
(PlanetaryEventStream for pub/sub messaging and event queue management)
"""

from collections.abc import Callable
from typing import Any

EVENT_TYPES = [
    "CycloneDetected",
    "FloodDetected",
    "HeatwaveDetected",
    "WildfireDetected",
    "VolcanoDetected",
    "EarthquakeDetected",
    "SolarStormDetected",
    "TornadoDetected",
    "HailDetected",
    "FlashFloodDetected",
    "LightningDetected",
    "DustStormDetected",
    "AirPollutionDetected",
]


class PlanetaryEventStream:
    """
    Bus d'événements géophysiques planétaires à priorité distribuée.
    """

    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = {evt: [] for evt in EVENT_TYPES}
        self.published_events_history: list[dict[str, Any]] = []

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """S'abonne à un type d'événement planétaire."""
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, payload: dict[str, Any], priority: str = "HIGH") -> dict[str, Any]:
        """Publie un événement géophysique sur le bus."""
        record = {"event_type": event_type, "priority": priority, "payload": payload}
        self.published_events_history.append(record)
        return {"status": "PUBLISHED", "event": record}
