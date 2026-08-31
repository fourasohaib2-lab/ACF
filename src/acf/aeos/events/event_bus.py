"""
Atmospheric Complexity Framework (ACF)

Planetary Event Bus Module (Phase 10)
(PlanetaryEventBus publish/subscribe system for Earth System events)
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class PlanetaryEvent:
    """Événement système planétaire."""

    event_id: str
    event_type: str  # ForecastUpdated, ObservationReceived, EarthquakeDetected, CycloneDetected, SolarStormDetected, FloodDetected, VolcanoDetected, AlertIssued, MissionCompleted
    payload: dict[str, Any]
    timestamp_utc: str


class PlanetaryEventBus:
    """
    Bus d'événements pub/sub planétaire permettant la communication asynchrone entre tous les microservices.
    """

    def __init__(self):
        self.subscribers: dict[str, list[Callable[[PlanetaryEvent], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[PlanetaryEvent], None]) -> None:
        """S'abonne à un type d'événement planétaire."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event: PlanetaryEvent) -> int:
        """Publie un événement planétaire à tous les abonnés."""
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            handler(event)
        return len(handlers)
