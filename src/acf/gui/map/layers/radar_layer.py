"""
Atmospheric Complexity Framework (ACF)

Radar Layer
===========

Weather radar layer.
"""

from .base_layer import BaseLayer


class RadarLayer(BaseLayer):
    """
    Weather radar layer.
    """

    ##################################################

    def __init__(self):

        super().__init__()

        self.name = "Radar"

        self.type = "radar"

        self.data = None

        self.alpha = 0.85

        self.colormap = "turbo"

        self.interpolation = "nearest"

        self.show_colorbar = True

        self.reflectivity_min = 0.0

        self.reflectivity_max = 75.0

    ##################################################

    def set_data(self, data):

        self.data = data

    ##################################################

    def clear(self):

        self.data = None

    ##################################################

    def render(self, renderer):
        """
        Render radar reflectivity.
        """

        if self.data is None:
            return

        renderer.render_raster(
            self.data,
            cmap=self.colormap,
            alpha=self.alpha,
            interpolation=self.interpolation,
            vmin=self.reflectivity_min,
            vmax=self.reflectivity_max,
            colorbar=self.show_colorbar,
        )

    ##################################################

    def status(self):

        return {
            "name": self.name,
            "type": self.type,
            "visible": self.visible,
            "opacity": self.opacity,
            "has_data": self.data is not None,
            "colormap": self.colormap,
            "alpha": self.alpha,
            "reflectivity_min": self.reflectivity_min,
            "reflectivity_max": self.reflectivity_max,
        }
