"""
Atmospheric Complexity Framework (ACF)

Satellite Layer
===============

Satellite imagery layer.
"""

from .base_layer import BaseLayer


class SatelliteLayer(BaseLayer):
    """
    Satellite imagery layer.
    """

    ##################################################

    def __init__(self):

        super().__init__()

        self.name = "Satellite"

        self.type = "satellite"

        self.data = None

        self.channel = "RGB"

        self.alpha = 1.0

        self.colormap = "gray"

        self.interpolation = "bilinear"

        self.show_colorbar = False

    ##################################################

    def set_data(self, data):

        self.data = data

    ##################################################

    def clear(self):

        self.data = None

    ##################################################

    def render(self, renderer):
        """
        Render satellite imagery.
        """

        if self.data is None:
            return

        renderer.render_raster(
            self.data,
            cmap=self.colormap,
            alpha=self.alpha,
            interpolation=self.interpolation,
        )

    ##################################################

    def status(self):

        return {
            "name": self.name,
            "type": self.type,
            "visible": self.visible,
            "opacity": self.opacity,
            "channel": self.channel,
            "has_data": self.data is not None,
            "colormap": self.colormap,
            "alpha": self.alpha,
        }
