"""Raster Renderer - For continuous data."""

from typing import Any

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

from .base_renderer import BaseRenderer


class RasterRenderer(BaseRenderer):
    """Renders raster data (temperature, precipitation, etc.)."""

    def __init__(self):
        super().__init__(name="RasterRenderer")
        self.colormap = "viridis"
        self.levels = None
        self._contourf = None
        self._colorbar = None

    def render(self, ax: Any, data: Any | None = None, **kwargs) -> Any:
        """Render raster data on the axes."""
        if data is None:
            return None

        # Extract data
        if hasattr(data, "values"):
            values = data.values
            lons = data.longitude.values if hasattr(data, "longitude") else None
            lats = data.latitude.values if hasattr(data, "latitude") else None
        else:
            values = data
            lons = kwargs.get("longitude")
            lats = kwargs.get("latitude")

        if lons is None or lats is None:
            raise ValueError("Longitude and latitude must be provided")

        if hasattr(values, "mask"):
            values = np.ma.masked_where(values.mask, values)

        cmap = kwargs.get("cmap", self.colormap)
        levels = kwargs.get("levels", self.levels)

        self._contourf = ax.contourf(
            lons,
            lats,
            values,
            levels=levels,
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            alpha=self.opacity,
            extend=kwargs.get("extend", "both"),
        )

        if kwargs.get("colorbar", True):
            label = kwargs.get("label", "")
            self._colorbar = plt.colorbar(
                self._contourf,
                ax=ax,
                orientation=kwargs.get("cbar_orientation", "horizontal"),
                pad=kwargs.get("cbar_pad", 0.05),
                label=label,
            )

        return self._contourf

    def clear(self) -> None:
        """Clear raster data."""
        self._contourf = None
        self._colorbar = None
