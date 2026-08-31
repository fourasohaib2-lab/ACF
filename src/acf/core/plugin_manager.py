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
        """Discover available plugins."""

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
