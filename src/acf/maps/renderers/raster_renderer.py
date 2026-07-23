"""
Raster Renderer
===============
"""


class RasterRenderer:

    def __init__(self):

        self.field = None
        self.colormap = "viridis"

        self.minimum = None
        self.maximum = None

        self.alpha = 1.0

    def set_field(self, field):

        self.field = field

    def has_field(self):

        return self.field is not None

    def set_colormap(self, name):

        self.colormap = name

    def set_range(self, minimum, maximum):

        self.minimum = minimum
        self.maximum = maximum

    def set_alpha(self, alpha):

        self.alpha = alpha

    def clear(self):

        self.field = None

    def render(self):

        if not self.has_field():
            return False

        return True

    def __repr__(self):

        return (
            f"RasterRenderer("
            f"colormap='{self.colormap}', "
            f"alpha={self.alpha})"
        )
