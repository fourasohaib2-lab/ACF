"""
ACF Cartopy Renderer Compatibility Shim
=======================================

Compatibility facade redirecting legacy `acf.visualization.cartopy_renderer`
to canonical `acf.maps.renderers.cartopy_renderer`.
"""

from acf.maps.renderers.cartopy_renderer import CartopyRenderer as CanonicalCartopyRenderer
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class CartopyRenderer(CanonicalCartopyRenderer):
    """
    Compatibility CartopyRenderer facade supporting both headless canvas
    and legacy direct figure creation methods.
    """

    def __init__(self, canvas=None):
        if canvas is not None:
            super().__init__(canvas)
        else:
            self.canvas = None
        self.figure = None
        self.axis = None
        self.layers = []

    def create_map(self):
        """Legacy figure creation helper."""
        self.figure = plt.figure(figsize=(10, 6))
        self.axis = plt.axes(projection=ccrs.PlateCarree())
        self.axis.set_global()
        self.axis.add_feature(cfeature.LAND)
        self.axis.add_feature(cfeature.OCEAN)
        self.axis.add_feature(cfeature.BORDERS)
        self.axis.add_feature(cfeature.COASTLINE)
        self.axis.gridlines(draw_labels=True)
        return self.figure, self.axis

    def add_field(self, longitude, latitude, data, colormap="viridis", levels=20):
        """Legacy field plotting helper."""
        if self.axis is None:
            raise RuntimeError("Map not initialized")
        layer = self.axis.contourf(
            longitude,
            latitude,
            data,
            levels=levels,
            cmap=colormap,
            transform=ccrs.PlateCarree(),
        )
        self.layers.append(layer)
        return layer

    def status(self):
        """Legacy status diagnostic information."""
        return {
            "figure": self.figure is not None,
            "axis": self.axis is not None,
            "layers": len(self.layers),
            "engine": "Cartopy",
        }


__all__ = ["CartopyRenderer"]
