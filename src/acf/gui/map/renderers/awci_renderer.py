"""
AWCI Renderer
=============

Renders AWCI complexity map on the canvas.
"""

from typing import Any

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

from .base_renderer import BaseRenderer


class AWCIRenderer(BaseRenderer):
    """
    Renders AWCI complexity map.

    Displays the Aviation Weather Complexity Index as
    a color-coded map.
    """

    COLORMAP = "RdYlBu_r"  # Red for high complexity, blue for low

    def __init__(self):
        super().__init__(name="AWCIRenderer")
        self.colormap = self.COLORMAP
        self._contourf = None
        self._colorbar = None
        self.levels = [0, 20, 35, 50, 65, 85, 100]
        self.level_labels = ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"]

    def _extract_arrays(self, data: dict):
        """
        Extract awci, longitude, latitude from dictionary with flexible key names.
        Returns tuple (awci, lons, lats) or raises ValueError.
        """
        # Extract awci
        awci = data.get("awci")
        if awci is None:
            raise ValueError("Missing 'awci' key in data dictionary")

        # Extract longitude
        lons = None
        for key in ["longitude", "lon", "lons", "lng"]:
            if key in data and data[key] is not None:
                lons = data[key]
                break

        # Extract latitude
        lats = None
        for key in ["latitude", "lat", "lats"]:
            if key in data and data[key] is not None:
                lats = data[key]
                break

        if lons is None:
            raise ValueError(
                "Longitude not found. Available keys: "
                + ", ".join(data.keys())
                + ". Expected one of: 'longitude', 'lon', 'lons', 'lng'"
            )
        if lats is None:
            raise ValueError(
                "Latitude not found. Available keys: "
                + ", ".join(data.keys())
                + ". Expected one of: 'latitude', 'lat', 'lats'"
            )

        return awci, lons, lats

    def render(self, ax: Any, data: dict | Any | None = None, **kwargs) -> Any:
        """Render AWCI complexity map."""
        if data is None:
            return None

        # Print diagnostic
        print(f"[AWCIRenderer] Type de data: {type(data)}")
        if isinstance(data, dict):
            print(f"[AWCIRenderer] Clés du dictionnaire: {list(data.keys())}")

        # Extract data - Check for dict FIRST
        if isinstance(data, dict):
            values, lons, lats = self._extract_arrays(data)
        elif hasattr(data, "values") and hasattr(data, "longitude"):
            # xarray DataArray
            values = data.values
            lons = data.longitude.values if hasattr(data, "longitude") else None
            lats = data.latitude.values if hasattr(data, "latitude") else None
            if lons is None or lats is None:
                raise ValueError("xarray data missing 'longitude' or 'latitude' coordinates")
        else:
            raise ValueError("Data must be dict or xarray.DataArray")

        # Handle masked arrays
        if hasattr(values, "mask"):
            values = np.ma.masked_where(values.mask, values)

        # Get levels and colormap
        levels = kwargs.get("levels", self.levels)
        cmap = kwargs.get("cmap", self.colormap)
        extend = kwargs.get("extend", "both")

        # Create the plot
        self._contourf = ax.contourf(
            lons,
            lats,
            values,
            levels=levels,
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            alpha=self.opacity,
            extend=extend,
        )

        # Add colorbar if requested
        if kwargs.get("colorbar", True):
            label = kwargs.get("label", "AWCI Complexity")
            orientation = kwargs.get("cbar_orientation", "horizontal")
            pad = kwargs.get("cbar_pad", 0.05)

            self._colorbar = plt.colorbar(
                self._contourf, ax=ax, orientation=orientation, pad=pad, label=label, ticks=levels
            )

            if len(levels) == len(self.level_labels) + 1:
                self._colorbar.set_ticklabels([""] + self.level_labels)

        return self._contourf

    def clear(self) -> None:
        """Clear rendered data."""
        self._contourf = None
        self._colorbar = None
