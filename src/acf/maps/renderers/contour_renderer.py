"""
Contour Renderer
================
"""


class ContourRenderer:

    def __init__(self):

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

    def render(self):

        if not self.has_field():
            return False

        return True

    def __repr__(self):

        return (
            f"ContourRenderer("
            f"levels={len(self.levels)}, "
            f"color='{self.color}')"
        )
