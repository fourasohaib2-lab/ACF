"""
ACF Cartopy Renderer Compatibility Shim
=======================================

Compatibility facade redirecting legacy `acf.visualization.cartopy_renderer`
to canonical `acf.maps.renderers.cartopy_renderer`.
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from acf.gui.map.mtg_basemap import draw_mtg_basemap
from acf.maps.renderers.cartopy_renderer import CartopyRenderer as CanonicalCartopyRenderer


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
        self._draw_basemap()
        self.axis.gridlines(draw_labels=True)
        return self.figure, self.axis

    def _draw_basemap(self) -> None:
        """Live MTG basemap (explicit user request "je veux que toutes
        les maps affiché soient des maps du mtg") - real EUMETSAT
        imagery when available, same acf.gui.map.mtg_basemap every
        other real map view uses. Falls back to the plain Land/Ocean
        fill when no image has been fetched yet - never a fabricated
        substitute image. Split out of create_map() so refresh_basemap()
        below can redraw just this part on a live image update without
        tearing down the figure/axis (and the QWidget canvas wrapping
        them - see acf.gui.widgets.map_view.MapView)."""
        has_mtg_image = draw_mtg_basemap(self.axis, zorder=0)
        if not has_mtg_image:
            self.axis.add_feature(cfeature.LAND)
            self.axis.add_feature(cfeature.OCEAN)
        self.axis.add_feature(cfeature.BORDERS)
        self.axis.add_feature(cfeature.COASTLINE)

    def refresh_basemap(self) -> None:
        """Redraw the basemap in place on a live MTG image update -
        MapView connects this to MTGBasemapProvider.updated so the
        Classic Dashboard's map picks up new imagery the same as every
        other real map view. No-op if create_map() was never called."""
        if self.axis is None:
            return
        self.axis.clear()
        self.axis.set_global()
        self._draw_basemap()
        self.axis.gridlines(draw_labels=True)

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

    def clear(self):
        """
        Legacy clear helper.

        NOTE (correction): create_map()/add_field()/status() are all
        overridden here for the canvas-less legacy mode, but clear()
        was not - a canvas-less instance (self.canvas is None, the
        default) inherited CanonicalCartopyRenderer.clear(), which
        unconditionally does self.canvas.figure.clear(), crashing with
        AttributeError: 'NoneType' object has no attribute 'figure'.
        Confirmed via acf.gui.widgets.map_view.MapView.clear() (this
        widget always constructs this class with no canvas).
        """
        if self.canvas is not None:
            super().clear()
            return
        if self.figure is not None:
            plt.close(self.figure)
        self.figure = None
        self.axis = None
        self.layers = []


__all__ = ["CartopyRenderer"]
