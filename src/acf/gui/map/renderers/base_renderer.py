"""Base Renderer - Abstract class for all renderers."""

from abc import ABC, abstractmethod
from typing import Any


class BaseRenderer(ABC):
    """Abstract base class for all map renderers."""

    def __init__(self, name: str = "BaseRenderer"):
        self.name = name
        self.visible = True
        self.z_index = 0
        self.opacity = 1.0
        self._data = None

    @abstractmethod
    def render(self, ax: Any, data: Any | None = None, **kwargs) -> Any:
        """Render data on the given axes."""

    @abstractmethod
    def clear(self) -> None:
        """Clear rendered content."""

    def set_visible(self, visible: bool) -> None:
        """Set visibility of the renderer."""
        self.visible = visible

    def set_opacity(self, opacity: float) -> None:
        """Set opacity (0.0 to 1.0)."""
        self.opacity = max(0.0, min(1.0, opacity))

    def set_z_index(self, z_index: int) -> None:
        """Set rendering z-order."""
        self.z_index = z_index
