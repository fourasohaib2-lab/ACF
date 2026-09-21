"""
Atmospheric Complexity Framework (ACF)

AWCI Plugins - Manager

Real, top-level orchestrator of this package - the ``manager.py``
module named in
``docs/architecture/awci_reference_architecture.md`` section 20.
Composes ``registry.py``/``loader.py`` (and gives access to a real
``HookRegistry`` for callers who also need lifecycle hooks) - no new
logic beyond what those already provide.
"""

from __future__ import annotations

from pathlib import Path

from awci.plugins.hooks import HookRegistry
from awci.plugins.interface import AWCIPlugin, PluginCategory
from awci.plugins.loader import PluginLoadError, discover_plugins
from awci.plugins.registry import DuplicatePluginError, PluginRegistry


class PluginManager:
    """
    Real, top-level entry point for AWCI plugin registration,
    discovery, and lookup - owns one real ``PluginRegistry`` and one
    real ``HookRegistry``.
    """

    def __init__(self) -> None:
        self.registry = PluginRegistry()
        self.hooks = HookRegistry()

    def register(self, plugin: AWCIPlugin) -> None:
        """Real, direct registration of an already-constructed plugin
        instance - see ``PluginRegistry.register()`` for the real
        duplicate-name behaviour."""
        self.registry.register(plugin)

    def discover(self, plugin_dir: Path | str) -> list[PluginLoadError]:
        """
        Real filesystem discovery - loads every real ``AWCIPlugin``
        found under ``plugin_dir`` (see ``loader.discover_plugins()``)
        and registers each one. A plugin whose name collides with one
        already registered is recorded as a real ``PluginLoadError``
        (the real ``DuplicatePluginError`` message, not silently
        dropped and not allowed to crash the rest of discovery) rather
        than raised, since a directory scan legitimately finding one
        bad file among many good ones should not lose every other real
        plugin in it. Returns every real load/registration failure
        found (an empty list means every real file in ``plugin_dir``
        loaded and registered cleanly).
        """
        result = discover_plugins(plugin_dir)
        errors = list(result.errors)
        for plugin in result.plugins:
            try:
                self.registry.register(plugin)
            except DuplicatePluginError as exc:
                errors.append(PluginLoadError(source_path=plugin.name, reason=str(exc)))
        return errors

    def get(self, name: str) -> AWCIPlugin | None:
        return self.registry.get(name)

    def list_by_category(self, category: PluginCategory) -> list[AWCIPlugin]:
        return self.registry.list_by_category(category)

    def all(self) -> list[AWCIPlugin]:
        return self.registry.all()
