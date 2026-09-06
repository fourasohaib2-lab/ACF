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
        """Publie un événement géophysique sur le bus.

        NOTE (correction — real functional gap, found during the
        post-model4d audit, 2026-09-06): a prior audit pass's own test
        comment claimed "PlanetaryEventStream is a genuine pub/sub
        implementation" because publish() genuinely recorded a real
        history entry (not a fabricated number) - but it never actually
        invoked any of the callbacks `subscribe()` collects into
        `self.subscribers[event_type]`. Subscribing then publishing the
        same event_type silently delivered nothing: `status: "PUBLISHED"`
        was claimed while zero subscribers were ever called - the
        entire point of a pub/sub bus. Verified no real caller in
        src/ depends on the previous (non-)dispatch behavior (only
        exported, otherwise unused outside its own test) - a real but
        previously-inert gap, not a behavior change for any existing
        caller. A subscriber callback that raises no longer prevents
        delivery to the others or crashes publish() itself; the
        exception is recorded per-subscriber instead of silently
        swallowed.
        """
        record = {"event_type": event_type, "priority": priority, "payload": payload}
        self.published_events_history.append(record)

        delivery_errors: list[str] = []
        for callback in self.subscribers.get(event_type, []):
            try:
                callback(payload)
            except Exception as exc:  # noqa: BLE001 - one bad subscriber must not break the others
                delivery_errors.append(f"{callback!r}: {exc}")

        return {
            "status": "PUBLISHED",
            "event": record,
            "subscribers_notified": len(self.subscribers.get(event_type, [])) - len(delivery_errors),
            "delivery_errors": delivery_errors,
        }
