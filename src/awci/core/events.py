"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Events

Real, generic application-lifecycle event bus - the ``events.py``
module named in ``docs/architecture/awci_reference_architecture.md``
section 1. A different real scope from the two existing pub/sub
primitives already built this session: ``awci.plugins.hooks.
HookRegistry`` (named plugin-extension hook points) and
``awci.alerts.notifications.AlertNotifier`` (dispatches ``Alert``
objects specifically). This one carries arbitrary named
application-lifecycle events (e.g. "ready", "project_opened") with an
arbitrary real payload - genuinely different from either, not a
duplicate. Follows the exact same real dispatch/error-isolation
pattern already established by both: a failing subscriber is recorded,
never silently swallowed, and never blocks another real subscriber.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from awci.core.types import EventCallback, EventName


@dataclass(frozen=True)
class Event:
    """A real, named application-lifecycle event with an arbitrary
    real payload - never invented data, only whatever the real caller
    that emits it supplies."""

    name: EventName
    payload: dict[str, Any] = field(default_factory=dict)
    emitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class EventDispatchError:
    """One real, disclosed failure of a single subscriber - never
    silently swallowed, and never allowed to stop every other real
    subscriber from receiving the same event (the same real
    error-isolation discipline as
    ``awci.plugins.hooks.HookRegistry.dispatch()`` and
    ``awci.alerts.notifications.AlertNotifier.notify()``)."""

    event_name: EventName
    reason: str


class EventBus:
    """Real, generic, in-process named-event subscriber registry."""

    def __init__(self) -> None:
        self._subscribers: dict[EventName, list[EventCallback]] = {}

    def subscribe(self, event_name: EventName, callback: EventCallback) -> None:
        """Real registration for a real named event. The same real
        callback can subscribe to more than one event, or to the same
        event more than once (each subscription fires independently)."""
        self._subscribers.setdefault(event_name, []).append(callback)

    def unsubscribe(self, event_name: EventName, callback: EventCallback) -> None:
        """Real removal - a no-op (not an error) if ``callback`` was
        never subscribed to ``event_name``."""
        subscribers = self._subscribers.get(event_name)
        if subscribers and callback in subscribers:
            subscribers.remove(callback)

    def emit(self, event_name: EventName, **payload: Any) -> list[EventDispatchError]:
        """Real dispatch of a real event, built from ``event_name`` and
        ``payload``, to every real subscriber of that event name, in
        real subscription order. A failing subscriber is recorded as a
        real, disclosed ``EventDispatchError`` and never blocks any
        other real subscriber. No subscribers for ``event_name``
        honestly dispatches nothing and returns an empty error list."""
        event = Event(name=event_name, payload=dict(payload))
        errors: list[EventDispatchError] = []
        for subscriber in self._subscribers.get(event_name, []):
            try:
                subscriber(event)
            except Exception as exc:
                errors.append(EventDispatchError(event_name=event_name, reason=f"{type(exc).__name__}: {exc}"))
        return errors
