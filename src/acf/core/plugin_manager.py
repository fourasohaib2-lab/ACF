"""
Atmospheric Complexity Framework (ACF)

Plugin Manager
"""

from pathlib import Path

from acf.core.logger import get_logger


class PluginManager:
    """Simple plugin manager."""

    def __init__(self, plugin_dir="plugins"):
        self.logger = get_logger()
        self.plugin_dir = Path(plugin_dir)
        self.plugins = []

    def discover(self):
        """Discover available plugins.

        NOTE (correction, 2026-09-04): used to append to `self.plugins`
        without clearing it first - a real, genuine bug, not just a
        theoretical one: any real caller re-scanning a real plugin
        directory more than once (e.g. a "rescan" UI action, or a
        second `discover()` call) accumulated real DUPLICATE entries
        rather than a genuine, up-to-date list. Now real, idempotent -
        the same true filesystem state every time.
        """
        self.plugins = []

        if not self.plugin_dir.exists():
            self.logger.warning("Plugin directory does not exist.")
            return

        for item in self.plugin_dir.iterdir():
            if item.is_dir():
                self.plugins.append(item.name)

        self.logger.info(f"{len(self.plugins)} plugin(s) found.")

    def list_plugins(self):
        """Return plugin names."""
        return self.plugins
