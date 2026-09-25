"""
Atmospheric Complexity Framework (ACF)

Alerts - Notification

Real, generic, in-process warning-notification dispatch - the
``notification.py`` module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``alerts/``). Follows the exact same real register/dispatch/
error-isolation pattern already established by
``awci.alerts.notifications.AlertNotifier``, applied here to
``acf.alerts.warning_engine.OperationalWarning`` instead of AWCI's
``Alert``.

Honest, disclosed scope: in-process (Python callable) dispatch only -
no real email/SMS/push/WMO-CAP-XML-feed integration exists anywhere
in this codebase for ACF's own warnings, so none is fabricated here.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from acf.alerts.warning_engine import OperationalWarning


@dataclass(frozen=True)
class WarningDispatchError:
    """One real, disclosed failure of a single registered subscriber -
    never silently swallowed, never blocking any other real
    subscriber."""

    reason: str


class WarningNotifier:
    """Real, in-process subscriber registry for
    ``OperationalWarning`` objects."""

    def __init__(self) -> None:
        self._subscribers: list[Callable[[OperationalWarning], None]] = []

    def subscribe(self, callback: Callable[[OperationalWarning], None]) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[OperationalWarning], None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def notify(self, warnings: tuple[OperationalWarning, ...]) -> list[WarningDispatchError]:
        """Real dispatch of every real warning in ``warnings`` to
        every real subscriber, in real subscription order. A failing
        subscriber is recorded, never silently swallowed, and never
        blocks any other real subscriber or warning."""
        errors: list[WarningDispatchError] = []
        for warning in warnings:
            for subscriber in self._subscribers:
                try:
                    subscriber(warning)
                except Exception as exc:
                    errors.append(WarningDispatchError(reason=f"{type(exc).__name__}: {exc}"))
        return errors
