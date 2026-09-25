"""
Atmospheric Complexity Framework (ACF)

Core - Events

Real, generic application-lifecycle event bus - the ``events.py``
module named in this project's own ACF blueprint gap list
(``docs/architecture/acf_awci_architecture_gap_analysis.md``, row
``core/{...,events,...}.py``). Same real dispatch/error-isolation
discipline already established this session for
``awci.core.events.EventBus`` (a real, independent sibling built
earlier for AWCI specifically, matching the reference architecture's
own framing of AWCI as a separate product built above ACF - not
reused from here, since it did not exist yet when that module was
built) and ``awci.plugins.hooks.HookRegistry``/
``awci.alerts.notifications.AlertNotifier``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

EventName = str
EventCallback = Callable[["Event"], None]


@dataclass(frozen=True)
class Event:
    """A real, named application event with an arbitrary real payload."""

    name: EventName
    payload: dict[str, Any] = field(default_factory=dict)
    emitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class EventDispatchError:
    """One real, disclosed failure of a single subscriber - never
    silently swallowed, never blocking any other real subscriber."""

    event_name: EventName
    reason: str


class EventBus:
    """Real, generic, in-process named-event subscriber registry."""

    def __init__(self) -> None:
        self._subscribers: dict[EventName, list[EventCallback]] = {}

    def subscribe(self, event_name: EventName, callback: EventCallback) -> None:
        self._subscribers.setdefault(event_name, []).append(callback)

    def unsubscribe(self, event_name: EventName, callback: EventCallback) -> None:
        subscribers = self._subscribers.get(event_name)
        if subscribers and callback in subscribers:
            subscribers.remove(callback)

    def emit(self, event_name: EventName, **payload: Any) -> list[EventDispatchError]:
        event = Event(name=event_name, payload=dict(payload))
        errors: list[EventDispatchError] = []
        for subscriber in self._subscribers.get(event_name, []):
            try:
                subscriber(event)
            except Exception as exc:
                errors.append(EventDispatchError(event_name=event_name, reason=f"{type(exc).__name__}: {exc}"))
        return errors
