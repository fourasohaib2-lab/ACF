"""
Atmospheric Complexity Framework (ACF)

Production Configuration Module
"""

from typing import Any


class ProductionConfiguration:
    """Gestionnaire de la configuration officielle de production d'ACF."""

    @classmethod
    def get_config(cls) -> dict[str, Any]:
        return {
            "environment": "PRODUCTION",
            "debug": False,
            "log_level": "INFO",
            "cache_dir": "/var/cache/acf",
            "max_threads": 64,
        }
