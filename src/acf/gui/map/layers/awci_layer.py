"""
Atmospheric Complexity Framework (ACF)

AWCI Layer
==========

Atmospheric Weather Complexity Index layer.
"""

from .base_layer import BaseLayer


class AWCILayer(BaseLayer):
    """
    Atmospheric Weather Complexity Index layer.
    """

    ##################################################

    def __init__(self):

        super().__init__()

        self.name = "AWCI"

        self.type = "awci"

        self.data = None

        self.colormap = "turbo"

        self.alpha = 0.90

        self.minimum = None

        self.maximum = None

        self.interpolation = "nearest"

        self.show_colorbar = True

        self.show_contours = False

        self.levels = 20

    ##################################################

    def set_data(self, data):

        self.data = data

    ##################################################

    def clear(self):

        self.data = None

    ##################################################

    def render(self, renderer):

        """
        Render AWCI layer.
        """

        if self.data is None:
            return

        renderer.render_awci(
            self.data,
            cmap=self.colormap,
            alpha=self.alpha,
            vmin=self.minimum,
            vmax=self.maximum,
            interpolation=self.interpolation,
            colorbar=self.show_colorbar,
            contours=self.show_contours,
            levels=self.levels,
        )

    ##################################################

    def status(self):

        return {

            "name": self.name,

            "visible": self.visible,

            "opacity": self.opacity,

            "has_data": self.data is not None,

            "colormap": self.colormap,

            "alpha": self.alpha,

            "levels": self.levels,

        }

