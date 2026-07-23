"""
Atmospheric Complexity Framework (ACF)
Configuration Manager
"""

from pathlib import Path
import yaml


class ConfigManager:
    """Loads and provides access to application configuration."""

    def __init__(self, filename: str = "config/config.yaml"):
        self.path = Path(filename)
        self.data = {}

    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.path}")

        with self.path.open("r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    def get(self, section: str, key: str, default=None):
        """Return a configuration value."""
        return self.data.get(section, {}).get(key, default)
