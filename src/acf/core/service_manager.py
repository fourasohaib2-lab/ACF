"""
Atmospheric Complexity Framework (ACF)

Service Manager
"""

from typing import Any


class ServiceManager:
    """Registry for shared application services."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """Register a service."""
        self._services[name] = service

    def get(self, name: str) -> Any:
        """Return a registered service."""
        if name not in self._services:
            raise KeyError(f"Service '{name}' is not registered.")
        return self._services[name]

    def exists(self, name: str) -> bool:
        """Check if a service exists."""
        return name in self._services

    def list_services(self) -> list[str]:
        """Return all registered service names."""
        return sorted(self._services.keys())
