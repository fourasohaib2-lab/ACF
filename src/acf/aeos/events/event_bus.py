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
    Bus d'événements pub/sub planétaire entre les services enregistrés dans acf.aeos.

    NOTE (Physics Guard, 2026-09-06 Tier E sweep): despite "communication
    asynchrone" above, publish() calls every subscribed handler
    synchronously and in-line (no thread/async dispatch) - a real,
    correct pub/sub pattern, just not asynchronous. Verified by grep:
    this whole class (like the rest of acf.aeos) is not constructed
    anywhere in src/ outside its own test, tests/test_aeos_platform.py.
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
