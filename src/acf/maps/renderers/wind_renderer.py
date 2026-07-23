"""
Wind Renderer
=============
"""


class WindRenderer:

    def __init__(self):

        self.u = None
        self.v = None

        self.color = "black"
        self.scale = 1.0

    def set_field(self, u, v):

        self.u = u
        self.v = v

    def clear(self):

        self.u = None
        self.v = None

    def has_field(self):

        return self.u is not None and self.v is not None

    def set_color(self, color):

        self.color = color

    def set_scale(self, scale):

        self.scale = scale

    def render(self):

        if not self.has_field():
            return False

        return True

    def __repr__(self):

        return (
            f"WindRenderer("
            f"color='{self.color}', "
            f"scale={self.scale})"
        )
