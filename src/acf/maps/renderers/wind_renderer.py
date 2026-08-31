"""
Wind Renderer
=============
"""


class WindRenderer:
    def __init__(self, canvas=None):

        self.canvas = canvas
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

    def render(self, u=None, v=None, *args, **kwargs):

        if u is not None and v is not None:
            self.set_field(u, v)

        return self.has_field()

    def __repr__(self):

        return f"WindRenderer(color='{self.color}', scale={self.scale})"
