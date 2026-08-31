"""Vector Renderer - For wind fields, currents, etc."""

from typing import Any

import cartopy.crs as ccrs

from .base_renderer import BaseRenderer


class VectorRenderer(BaseRenderer):
    """Renders vector fields (wind, currents, etc.)."""

    def __init__(self):
        super().__init__(name="VectorRenderer")
        self.color = "black"
        self.scale = 1.0
        self._quiver = None

    def render(self, ax: Any, data: Any | None = None, **kwargs) -> Any:
        """Render vector field on the axes."""
        if data is None:
            return None

        if hasattr(data, "u"):
            u = data.u.values if hasattr(data.u, "values") else data.u
            v = data.v.values if hasattr(data.v, "values") else data.v
            lon = data.longitude.values if hasattr(data, "longitude") else None
            lat = data.latitude.values if hasattr(data, "latitude") else None
        elif isinstance(data, tuple) and len(data) == 4:
            u, v, lon, lat = data
        else:
            raise ValueError("Data must have u, v, lon, lat attributes or be a tuple")

        if lon is None or lat is None:
            raise ValueError("Longitude and latitude must be provided")

        self._quiver = ax.quiver(
            lon,
            lat,
            u,
            v,
            transform=ccrs.PlateCarree(),
            color=kwargs.get("color", self.color),
            scale=kwargs.get("scale", self.scale),
            alpha=self.opacity,
        )

        return self._quiver

    def clear(self) -> None:
        """Clear vector field."""
        self._quiver = None
