"""
Atmospheric Complexity Framework (ACF)

AWCI Plugins - Hooks

Real lifecycle hook dispatch - the ``hooks.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 20, so a
real plugin can react to a real AWCI lifecycle event ("a new hazard
computed", "a new model run completed", ...) without the core needing
to know that plugin exists ahead of time.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HookCallError:
    """One real, disclosed failure of a single registered callback -
    never silently swallowed, and never allowed to stop every other
    real callback registered for the same hook from running (the same
    real error-isolation discipline as ``loader.py``'s own broad
    ``except Exception``, for the same reason: a hook callback is
    real, caller-supplied code)."""

    hook_name: str
    reason: str


class HookRegistry:
    """Real, in-memory named-hook dispatcher - any number of real
    callbacks can be registered per real hook name; dispatching a hook
    calls every one of them and collects both real results and real,
    disclosed failures, never silently dropping either."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[..., Any]]] = {}

    def register(self, hook_name: str, callback: Callable[..., Any]) -> None:
        """Real registration - the same real callback object can be
        registered under several real hook names, and several real
        callbacks can share one real hook name; order of registration
        is the real order ``dispatch()`` calls them in."""
        self._hooks.setdefault(hook_name, []).append(callback)

    def unregister(self, hook_name: str, callback: Callable[..., Any]) -> None:
        """Real removal - a no-op (not an error) if ``callback`` was
        never registered under ``hook_name``."""
        callbacks = self._hooks.get(hook_name)
        if callbacks is not None and callback in callbacks:
            callbacks.remove(callback)

    def registered_hook_names(self) -> list[str]:
        """Real, sorted list of every hook name with at least one real
        callback registered - empty when none is."""
        return sorted(name for name, callbacks in self._hooks.items() if callbacks)

    def dispatch(self, hook_name: str, **kwargs: Any) -> tuple[list[Any], list[HookCallError]]:
        """
        Real dispatch of ``hook_name`` to every real callback
        registered for it, in real registration order, with real
        keyword arguments forwarded unchanged. Returns every real
        successful callback's own real return value, plus every real,
        disclosed failure (never silently swallowed) - a failing
        callback never prevents any other real callback from running.
        An unregistered ``hook_name`` honestly returns two empty lists
        (never a fabricated result).
        """
        results: list[Any] = []
        errors: list[HookCallError] = []
        for callback in self._hooks.get(hook_name, []):
            try:
                results.append(callback(**kwargs))
            except Exception as exc:
                errors.append(HookCallError(hook_name=hook_name, reason=f"{type(exc).__name__}: {exc}"))
        return results, errors
