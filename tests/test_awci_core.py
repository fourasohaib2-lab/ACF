"""Tests for the new AWCI core (src/awci/core/), built while working
through the full remaining-gaps list ("On les attaque toutes un par
un") after it was identified as the specific gap in
docs/architecture/acf_awci_architecture_gap_analysis.md ("No dedicated
AWCI application/lifecycle/registry core exists; AWCI code is simply
part of acf.*'s own process").

AWCILifecycle.start() constructs a real AWCIWorkspaceManager(), whose
default recent-projects file lives under the real user's
~/.awci/recent_projects.json (see tests/test_awci_workspace.py for the
same isolation concern) - every test here that starts a real lifecycle
monkeypatches Path.home() to a real tmp_path first, never touching the
actual user's home directory.
"""

from __future__ import annotations

import pytest

from awci.core import (
    AWCIApplication,
    AWCIConfigurationError,
    AWCIContext,
    AWCIError,
    AWCILifecycle,
    AWCILifecycleError,
    AWCIServiceError,
    Event,
    EventBus,
    EventDispatchError,
    ServiceRegistry,
)
from awci.core.registry import ServiceRegistry as RegistryDirectImport
from awci.workspace import AWCIWorkspaceManager

# --------------------------------------------------------------------- events.py


def test_event_bus_dispatches_to_every_real_subscriber():
    bus = EventBus()
    received_a: list[str] = []
    received_b: list[str] = []
    bus.subscribe("ready", lambda e: received_a.append(e.name))
    bus.subscribe("ready", lambda e: received_b.append(e.payload.get("who", "")))

    errors = bus.emit("ready", who="test")

    assert received_a == ["ready"]
    assert received_b == ["test"]
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
    assert errors[0].event_name == "x"
    assert "ValueError" in errors[0].reason


def test_event_bus_with_no_subscribers_dispatches_nothing():
    bus = EventBus()
    assert bus.emit("nobody_listening") == []


def test_event_bus_unsubscribe_stops_future_dispatch():
    bus = EventBus()
    received: list[str] = []

    def callback(event: Event) -> None:
        received.append(event.name)

    bus.subscribe("x", callback)
    bus.unsubscribe("x", callback)
    bus.emit("x")

    assert received == []


def test_event_bus_unsubscribe_is_a_real_noop_when_absent():
    bus = EventBus()
    bus.unsubscribe("never_subscribed", lambda e: None)  # must not raise


def test_event_carries_a_real_timestamp():
    bus = EventBus()
    captured: list[Event] = []
    bus.subscribe("x", captured.append)
    bus.emit("x")
    assert captured[0].emitted_at


# --------------------------------------------------------------------- registry.py


def test_service_registry_is_the_real_reused_service_manager():
    from acf.core.service_manager import ServiceManager

    assert ServiceRegistry is ServiceManager
    assert RegistryDirectImport is ServiceManager


def test_service_registry_register_and_get():
    registry = ServiceRegistry()
    registry.register("logger", "fake-logger")
    assert registry.get("logger") == "fake-logger"
    assert registry.exists("logger")
    assert not registry.exists("missing")


# --------------------------------------------------------------------- context.py


def test_awci_context_defaults_to_no_open_project():
    context = AWCIContext()
    assert context.project is None
    assert context.has_project() is False


def test_awci_context_has_project_reflects_a_real_assigned_project(tmp_path, monkeypatch):
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: tmp_path)
    manager = AWCIWorkspaceManager()
    project = manager.create_project(name="Demo", directory=tmp_path)

    context = AWCIContext()
    context.project = project

    assert context.has_project() is True


# --------------------------------------------------------------------- lifecycle.py / application.py


def test_lifecycle_start_registers_real_services(tmp_path, monkeypatch):
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: tmp_path)

    lifecycle = AWCILifecycle()
    assert not lifecycle.is_started

    context = lifecycle.start()

    assert lifecycle.is_started
    assert context.services.exists("logger")
    assert context.services.exists("workspace")
    assert isinstance(context.services.get("workspace"), AWCIWorkspaceManager)


def test_lifecycle_start_registers_extra_services(tmp_path, monkeypatch):
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: tmp_path)

    lifecycle = AWCILifecycle()
    context = lifecycle.start(extra_services={"plugins": "fake-plugin-manager"})

    assert context.services.get("plugins") == "fake-plugin-manager"


def test_lifecycle_emits_starting_and_ready_events(tmp_path, monkeypatch):
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: tmp_path)

    lifecycle = AWCILifecycle()
    seen: list[str] = []
    # subscribe on the bus that will be used - it is created fresh in __init__
    lifecycle.context.events.subscribe("starting", lambda e: seen.append(e.name))
    lifecycle.context.events.subscribe("ready", lambda e: seen.append(e.name))

    lifecycle.start()

    assert seen == ["starting", "ready"]


def test_lifecycle_stop_raises_if_never_started():
    lifecycle = AWCILifecycle()
    with pytest.raises(AWCILifecycleError):
        lifecycle.stop()


def test_lifecycle_stop_emits_stopping_and_stopped(tmp_path, monkeypatch):
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: tmp_path)

    lifecycle = AWCILifecycle()
    lifecycle.start()
    seen: list[str] = []
    lifecycle.context.events.subscribe("stopping", lambda e: seen.append(e.name))
    lifecycle.context.events.subscribe("stopped", lambda e: seen.append(e.name))

    lifecycle.stop()

    assert seen == ["stopping", "stopped"]
    assert not lifecycle.is_started


def test_awci_application_start_stop_full_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr("awci.workspace.manager.Path.home", lambda: tmp_path)

    app = AWCIApplication()
    assert app.name == "AWCI"
    assert not app.is_running

    context = app.start()

    assert app.is_running
    assert context.services.exists("workspace")
    assert app.context is context

    app.stop()
    assert not app.is_running


# --------------------------------------------------------------------- exceptions.py / configuration.py


def test_awci_error_hierarchy_is_a_real_sibling_of_acf_error_not_a_subclass():
    from acf.core.exceptions import ACFError

    assert not issubclass(AWCIError, ACFError)
    assert issubclass(AWCIConfigurationError, AWCIError)
    assert issubclass(AWCIServiceError, AWCIError)
    assert issubclass(AWCILifecycleError, AWCIError)


def test_configuration_module_reuses_the_real_complexity_config_loader():
    import awci.core.configuration as configuration_module
    from awci.complexity.config_loader import AWCIConfig, load_config, save_default_config

    assert configuration_module.AWCIConfig is AWCIConfig
    assert configuration_module.load_config is load_config
    assert configuration_module.save_default_config is save_default_config


# --------------------------------------------------------------------- discipline


def test_awci_core_package_is_headless_no_gui_dependency_imported():
    import sys

    import awci.core  # noqa: F401

    core_module_names = [name for name in sys.modules if name.startswith("awci.core")]
    assert len(core_module_names) >= 9
    for name in core_module_names:
        module = sys.modules[name]
        source_file = getattr(module, "__file__", "") or ""
        assert "PySide6" not in source_file
