"""
Contour Renderer
================
"""


class ContourRenderer:
    def __init__(self, canvas=None):

        self.canvas = canvas
        self.field = None
        self.levels = []

        self.color = "black"
        self.linewidth = 1.0

    def set_field(self, field):

        self.field = field

    def set_levels(self, levels):

        self.levels = list(levels)

    def set_color(self, color):

        self.color = color

    def set_linewidth(self, width):

        self.linewidth = width

    def clear(self):

        self.field = None
        self.levels.clear()

    def has_field(self):

        return self.field is not None

    def render(self, field=None, *args, **kwargs):

        if field is not None:
            self.set_field(field)

        return self.has_field()

    def __repr__(self):

        return f"ContourRenderer(levels={len(self.levels)}, color='{self.color}')"
