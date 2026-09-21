"""Tests for the new ACF core additions (src/acf/core/events.py,
registry.py, lifecycle.py, context.py), built while working through
the full remaining-gaps list ("On les attaque toutes un par un") for
the ACF-general (not AWCI) gap: docs/architecture/
acf_awci_architecture_gap_analysis.md's own core/{...} row named
lifecycle.py/registry.py/events.py/context.py as missing from
src/acf/core/, distinct from acf.core.parameter_registry.py (science-
specific, not a generic registry).

registry.py/lifecycle.py are real aliases (Registry = ServiceManager,
Lifecycle = Bootstrap) - reusing already-real classes rather than
duplicating them; these tests lock in the identity, not new behavior.
events.py/context.py are genuinely new, generic content.
"""

from __future__ import annotations

from acf.core.bootstrap import Bootstrap
from acf.core.context import ApplicationContext
from acf.core.events import Event, EventBus, EventDispatchError
from acf.core.lifecycle import Lifecycle
from acf.core.registry import Registry
from acf.core.service_manager import ServiceManager


def test_registry_is_the_real_reused_service_manager():
    assert Registry is ServiceManager


def test_lifecycle_is_the_real_reused_bootstrap():
    assert Lifecycle is Bootstrap


def test_event_bus_dispatches_to_every_real_subscriber():
    bus = EventBus()
    received: list[str] = []
    bus.subscribe("ready", lambda e: received.append(e.payload.get("who", "")))
    errors = bus.emit("ready", who="test")
    assert received == ["test"]
    assert errors == []


def test_event_bus_isolates_a_failing_subscriber():
    bus = EventBus()
    received: list[str] = []
    bus.subscribe("x", lambda e: received.append("before"))

    def boom(event: Event) -> None:
        raise ValueError("nope")

    bus.subscribe("x", boom)
    bus.subscribe("x", lambda e: received.append("after"))

    errors = bus.emit("x")

    assert received == ["before", "after"]
    assert len(errors) == 1
    assert isinstance(errors[0], EventDispatchError)


def test_event_bus_unsubscribe_stops_future_dispatch():
    bus = EventBus()
    received: list[str] = []

    def callback(event: Event) -> None:
        received.append(event.name)

    bus.subscribe("x", callback)
    bus.unsubscribe("x", callback)
    bus.emit("x")
    assert received == []


def test_application_context_bundles_a_real_registry_and_event_bus():
    context = ApplicationContext()
    context.services.register("logger", "fake-logger")
    assert context.services.get("logger") == "fake-logger"

    received: list[str] = []
    context.events.subscribe("ready", lambda e: received.append(e.name))
    context.events.emit("ready")
    assert received == ["ready"]


def test_application_context_defaults_to_independent_instances():
    """Two separate ApplicationContext() instances must not share
    state - each gets its own real Registry/EventBus (mutable default
    factories, not a shared class-level mutable default)."""
    a = ApplicationContext()
    b = ApplicationContext()
    a.services.register("x", 1)
    assert not b.services.exists("x")
