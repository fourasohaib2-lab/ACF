"""Tests for the new AWCI plugin extension mechanism (src/awci/plugins/),
built while working through the full remaining-gaps list ("On les
attaque toutes un par un") after it was identified as a genuinely
absent piece in docs/architecture/acf_awci_architecture_gap_analysis.md
("awci/plugins/ | Not found.").

A pure software-engineering package (no scientific content), following
the same real, already-established ABC + register/get pattern already
used by acf.ai.plugins.base_plugin.AIPlugin/
acf.ai.plugins.plugin_manager.PluginManager. No fake "example" plugin
ships in src/ - test-only plugins are defined here instead.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from awci.plugins import (
    AWCIPlugin,
    DuplicatePluginError,
    HookRegistry,
    PluginCategory,
    PluginManager,
    PluginRegistry,
    discover_plugins,
)


class _EchoPlugin(AWCIPlugin):
    """Minimal, test-only plugin implementation."""

    name = "echo"
    category = PluginCategory.HAZARD
    version = "0.1"

    def describe(self) -> str:
        return "a real, minimal test-only plugin"


class _OtherEchoPlugin(AWCIPlugin):
    name = "other-echo"
    category = PluginCategory.VISUALIZATION

    def describe(self) -> str:
        return "a second, distinct test-only plugin"


# --------------------------------------------------------------------- interface


def test_plugin_category_covers_the_six_real_blueprint_categories():
    assert {c.value for c in PluginCategory} == {
        "data_source",
        "model",
        "hazard",
        "visualization",
        "aviation_product",
        "ai_agent",
    }


def test_awci_plugin_cannot_be_instantiated_without_describe():
    class _Incomplete(AWCIPlugin):
        name = "incomplete"
        category = PluginCategory.MODEL

    with pytest.raises(TypeError):
        _Incomplete()  # type: ignore[abstract]


def test_plugin_version_defaults_to_the_honest_unknown_sentinel():
    assert _OtherEchoPlugin.version == "unknown"
    assert _EchoPlugin.version == "0.1"


# --------------------------------------------------------------------- registry


def test_registry_register_and_get():
    registry = PluginRegistry()
    plugin = _EchoPlugin()
    registry.register(plugin)
    assert registry.get("echo") is plugin
    assert len(registry) == 1
    assert "echo" in registry


def test_registry_get_returns_none_for_unknown_name():
    registry = PluginRegistry()
    assert registry.get("nothing-here") is None


def test_registry_rejects_duplicate_names():
    registry = PluginRegistry()
    registry.register(_EchoPlugin())
    with pytest.raises(DuplicatePluginError):
        registry.register(_EchoPlugin())


def test_registry_unregister_is_a_real_noop_for_an_absent_name():
    registry = PluginRegistry()
    registry.unregister("never-registered")  # must not raise


def test_registry_list_by_category_is_sorted_and_scoped():
    registry = PluginRegistry()
    registry.register(_EchoPlugin())
    registry.register(_OtherEchoPlugin())
    hazard_plugins = registry.list_by_category(PluginCategory.HAZARD)
    assert [p.name for p in hazard_plugins] == ["echo"]
    viz_plugins = registry.list_by_category(PluginCategory.VISUALIZATION)
    assert [p.name for p in viz_plugins] == ["other-echo"]
    assert registry.list_by_category(PluginCategory.AI_AGENT) == []


def test_registry_all_is_sorted_by_name():
    registry = PluginRegistry()
    registry.register(_OtherEchoPlugin())
    registry.register(_EchoPlugin())
    assert [p.name for p in registry.all()] == ["echo", "other-echo"]


# --------------------------------------------------------------------- loader


def test_discover_plugins_loads_a_real_plugin_from_disk(tmp_path: Path):
    (tmp_path / "hello.py").write_text(
        "from awci.plugins.interface import AWCIPlugin, PluginCategory\n"
        "class HelloPlugin(AWCIPlugin):\n"
        "    name = 'hello'\n"
        "    category = PluginCategory.HAZARD\n"
        "    def describe(self):\n"
        "        return 'real disk-loaded plugin'\n"
    )
    result = discover_plugins(tmp_path)
    assert result.errors == ()
    assert len(result.plugins) == 1
    assert result.plugins[0].name == "hello"
    assert result.plugins[0].describe() == "real disk-loaded plugin"


def test_discover_plugins_reports_a_broken_file_without_losing_others(tmp_path: Path):
    (tmp_path / "good.py").write_text(
        "from awci.plugins.interface import AWCIPlugin, PluginCategory\n"
        "class GoodPlugin(AWCIPlugin):\n"
        "    name = 'good'\n"
        "    category = PluginCategory.MODEL\n"
        "    def describe(self):\n"
        "        return 'good'\n"
    )
    (tmp_path / "broken.py").write_text("raise RuntimeError('boom')\n")
    result = discover_plugins(tmp_path)
    assert [p.name for p in result.plugins] == ["good"]
    assert len(result.errors) == 1
    assert "broken.py" in result.errors[0].source_path
    assert "RuntimeError" in result.errors[0].reason
    assert "boom" in result.errors[0].reason


def test_discover_plugins_skips_underscore_prefixed_files(tmp_path: Path):
    (tmp_path / "_private.py").write_text("raise RuntimeError('must never be imported')\n")
    result = discover_plugins(tmp_path)
    assert result.plugins == ()
    assert result.errors == ()


def test_discover_plugins_on_a_nonexistent_directory_reports_one_honest_error(tmp_path: Path):
    result = discover_plugins(tmp_path / "does-not-exist")
    assert result.plugins == ()
    assert len(result.errors) == 1
    assert "not a real directory" in result.errors[0].reason


def test_discover_plugins_never_indexes_an_imported_but_not_defined_class(tmp_path: Path):
    """Same "only the true defining module" discipline as
    awci.ai.rag.documents - a file that merely imports AWCIPlugin
    itself (without subclassing it) must not produce a phantom
    plugin."""
    (tmp_path / "just_imports.py").write_text("from awci.plugins.interface import AWCIPlugin\n")
    result = discover_plugins(tmp_path)
    assert result.plugins == ()
    assert result.errors == ()


# --------------------------------------------------------------------- hooks


def test_hook_registry_dispatch_calls_every_real_callback_in_order():
    registry = HookRegistry()
    calls: list[str] = []
    registry.register("on_event", lambda: calls.append("first"))
    registry.register("on_event", lambda: calls.append("second"))
    results, errors = registry.dispatch("on_event")
    assert calls == ["first", "second"]
    assert errors == []
    assert results == [None, None]


def test_hook_registry_dispatch_passes_real_kwargs():
    registry = HookRegistry()
    registry.register("on_score", lambda score, level: f"{level}:{score}")
    results, _errors = registry.dispatch("on_score", score=42, level="High")
    assert results == ["High:42"]


def test_hook_registry_isolates_a_failing_callback_from_the_rest():
    registry = HookRegistry()
    registry.register("on_event", lambda: "ok-before")

    def boom() -> None:
        raise ValueError("nope")

    registry.register("on_event", boom)
    registry.register("on_event", lambda: "ok-after")
    results, errors = registry.dispatch("on_event")
    assert results == ["ok-before", "ok-after"]
    assert len(errors) == 1
    assert errors[0].hook_name == "on_event"
    assert "ValueError" in errors[0].reason
    assert "nope" in errors[0].reason


def test_hook_registry_dispatch_on_unregistered_hook_is_honestly_empty():
    registry = HookRegistry()
    results, errors = registry.dispatch("never-registered")
    assert results == []
    assert errors == []


def test_hook_registry_unregister_is_a_real_noop_when_absent():
    registry = HookRegistry()
    registry.unregister("nothing", lambda: None)  # must not raise


def test_hook_registry_registered_hook_names_is_sorted():
    registry = HookRegistry()
    registry.register("zeta", lambda: None)
    registry.register("alpha", lambda: None)
    assert registry.registered_hook_names() == ["alpha", "zeta"]


# --------------------------------------------------------------------- manager


def test_plugin_manager_register_and_get():
    manager = PluginManager()
    manager.register(_EchoPlugin())
    assert manager.get("echo") is not None
    assert manager.get("echo").describe() == "a real, minimal test-only plugin"


def test_plugin_manager_discover_registers_every_real_loaded_plugin(tmp_path: Path):
    (tmp_path / "hello.py").write_text(
        "from awci.plugins.interface import AWCIPlugin, PluginCategory\n"
        "class HelloPlugin(AWCIPlugin):\n"
        "    name = 'hello'\n"
        "    category = PluginCategory.AI_AGENT\n"
        "    def describe(self):\n"
        "        return 'hi'\n"
    )
    manager = PluginManager()
    errors = manager.discover(tmp_path)
    assert errors == []
    assert manager.get("hello") is not None
    assert manager.list_by_category(PluginCategory.AI_AGENT)[0].name == "hello"


def test_plugin_manager_discover_reports_duplicate_names_without_crashing(tmp_path: Path):
    manager = PluginManager()
    manager.register(_EchoPlugin())
    (tmp_path / "dup.py").write_text(
        "from awci.plugins.interface import AWCIPlugin, PluginCategory\n"
        "class DupPlugin(AWCIPlugin):\n"
        "    name = 'echo'\n"
        "    category = PluginCategory.HAZARD\n"
        "    def describe(self):\n"
        "        return 'duplicate'\n"
    )
    errors = manager.discover(tmp_path)
    assert len(errors) == 1
    assert "already registered" in errors[0].reason
    # The original registration must survive untouched.
    assert manager.get("echo").describe() == "a real, minimal test-only plugin"


def test_plugin_manager_all_and_list_by_category():
    manager = PluginManager()
    manager.register(_EchoPlugin())
    manager.register(_OtherEchoPlugin())
    assert [p.name for p in manager.all()] == ["echo", "other-echo"]
    assert [p.name for p in manager.list_by_category(PluginCategory.VISUALIZATION)] == ["other-echo"]


def test_plugin_manager_owns_its_own_real_hook_registry():
    manager = PluginManager()
    assert isinstance(manager.hooks, HookRegistry)
    manager.hooks.register("ping", lambda: "pong")
    results, _errors = manager.hooks.dispatch("ping")
    assert results == ["pong"]


# --------------------------------------------------------------------- discipline


def test_no_real_awci_module_is_shipped_as_a_default_plugin():
    """Honest, disclosed scope: this package ships zero registered
    plugins by default - real extensions are added by a real caller,
    never fabricated here."""
    manager = PluginManager()
    assert manager.all() == []
