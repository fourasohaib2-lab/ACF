"""
Atmospheric Complexity Framework (ACF)

AWCI Plugins - Registry

Real, in-memory plugin registry - the ``registry.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 20.
Duplicate registration is a real, disclosed error (never a silent
overwrite - matching the same discipline already established by
``awci.complexity.calibration.ValidationOverlapError``: a real
programming mistake should raise, not be quietly accepted).
"""

from __future__ import annotations

from awci.plugins.interface import AWCIPlugin, PluginCategory


class DuplicatePluginError(ValueError):
    """Raised when a plugin name is registered twice - a real
    programming mistake (two extensions accidentally sharing a name),
    never silently resolved by keeping the second one."""


class PluginRegistry:
    """Real, in-memory plugin registry - one real ``AWCIPlugin``
    instance per real, unique name."""

    def __init__(self) -> None:
        self._plugins: dict[str, AWCIPlugin] = {}

    def register(self, plugin: AWCIPlugin) -> None:
        """Real registration - raises ``DuplicatePluginError`` if
        ``plugin.name`` is already registered, never silently
        replacing the existing entry."""
        if plugin.name in self._plugins:
            raise DuplicatePluginError(f"A plugin named {plugin.name!r} is already registered.")
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """Real removal - a no-op (not an error) when ``name`` was
        never registered, matching this codebase's own established
        "removing something already absent is not itself a failure"
        convention."""
        self._plugins.pop(name, None)

    def get(self, name: str) -> AWCIPlugin | None:
        """Real lookup by name - ``None`` (never a fabricated default
        plugin) when ``name`` is not registered."""
        return self._plugins.get(name)

    def list_by_category(self, category: PluginCategory) -> list[AWCIPlugin]:
        """Real, sorted-by-name list of every registered plugin in
        ``category`` - an empty list (never fabricated) when none is
        registered for it."""
        return sorted((p for p in self._plugins.values() if p.category == category), key=lambda p: p.name)

    def all(self) -> list[AWCIPlugin]:
        """Real, sorted-by-name list of every registered plugin."""
        return sorted(self._plugins.values(), key=lambda p: p.name)

    def __len__(self) -> int:
        return len(self._plugins)

    def __contains__(self, name: str) -> bool:
        return name in self._plugins
