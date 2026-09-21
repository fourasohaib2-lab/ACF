"""
Atmospheric Complexity Framework (ACF)

AWCI Alerts - Notifications

Real, generic, in-process alert-notification dispatch - the
``notifications.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 19.
Follows the same real register/dispatch pattern already established
by ``awci.plugins.hooks.HookRegistry`` (a real precedent already built
this session), specialized to ``Alert`` objects.

Honest, disclosed scope: this is in-process (Python callable) dispatch
only - no real email/SMS/push/Slack integration exists anywhere in
this codebase for AWCI alerts specifically, so none is fabricated
here. A real caller wires this to whatever real channel it has (e.g. a
GUI toast, a log sink, a future real webhook).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from awci.alerts.engine import Alert


@dataclass(frozen=True)
class NotificationDispatchError:
    """One real, disclosed failure of a single registered subscriber -
    never silently swallowed, and never allowed to stop every other
    real subscriber from running (the same real error-isolation
    discipline as ``awci.plugins.hooks.HookRegistry.dispatch()``, for
    the same reason: a subscriber is real, caller-supplied code)."""

    reason: str


class AlertNotifier:
    """
    Real, in-process subscriber registry - any number of real
    callables can subscribe; ``notify()`` calls every one of them with
    every real alert supplied.
    """

    def __init__(self) -> None:
        self._subscribers: list[Callable[[Alert], None]] = []

    def subscribe(self, callback: Callable[[Alert], None]) -> None:
        """Real registration - the same real callback can be
        subscribed more than once (each subscription fires
        independently); order of subscription is the real order
        ``notify()`` calls them in."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Alert], None]) -> None:
        """Real removal - a no-op (not an error) if ``callback`` was
        never subscribed."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def notify(self, alerts: tuple[Alert, ...]) -> list[NotificationDispatchError]:
        """
        Real dispatch of every real alert in ``alerts`` to every real
        subscriber, in real subscription order. A failing subscriber
        is recorded as a real, disclosed ``NotificationDispatchError``
        (never silently swallowed) and never blocks any other real
        subscriber or any other real alert from being dispatched. An
        empty ``alerts`` tuple or no real subscribers honestly
        dispatches nothing and returns an empty error list.
        """
        errors: list[NotificationDispatchError] = []
        for alert in alerts:
            for subscriber in self._subscribers:
                try:
                    subscriber(alert)
                except Exception as exc:
                    errors.append(NotificationDispatchError(reason=f"{type(exc).__name__}: {exc}"))
        return errors
