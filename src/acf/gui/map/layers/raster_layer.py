"""
Atmospheric Complexity Framework (ACF)

Raster Layer
============

Generic raster layer.

Examples
--------
- Temperature
- Pressure
- Humidity
- AWCI Grid
- DEM
"""

from .base_layer import BaseLayer


class RasterLayer(BaseLayer):
    """
    Generic raster layer.
    """

    ##################################################

    def __init__(
        self,
        name="Raster",
        data=None,
    ):

        super().__init__(name)

        self.data = data

        self.colormap = "viridis"

        self.opacity = 1.0

        self.interpolation = "nearest"

    ##################################################

    def render(
        self,
        renderer,
    ):
        """
        Ask renderer to draw raster.
        """

        if renderer is None:
            return

        if self.data is None:
            return

        renderer.render_raster(
            self.data,
            cmap=self.colormap,
            alpha=self.opacity,
            interpolation=self.interpolation,
        )

    ##################################################

    def set_data(
        self,
        data,
    ):

        self.data = data

    ##################################################

    def status(self):

        status = super().status()

        status.update(
            {
                "type": "RasterLayer",
                "has_data": self.data is not None,
                "colormap": self.colormap,
                "opacity": self.opacity,
            }
        )

        return status
