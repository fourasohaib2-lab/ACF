"""
Atmospheric Complexity Framework (ACF)
Canvas
=====================================
"""
from .map_canvas import MapCanvas

__all__ = ["MapCanvas"]

class Canvas:
    """Surface de dessin pour les cartes météorologiques."""

    def __init__(
        self,
        width: int = 1200,
        height: int = 800,
        dpi: int = 100,
        background: str = "white",
    ):
        self.width = width
        self.height = height
        self.dpi = dpi
        self.background = background

        self.figure = None
        self.renderer = None

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height

    def size(self):
        return (self.width, self.height)

    def set_background(self, color: str):
        self.background = color

    def set_dpi(self, dpi: int):
        self.dpi = dpi

    def attach_figure(self, figure):
        self.figure = figure

    def attach_renderer(self, renderer):
        self.renderer = renderer

    def clear(self):
        self.figure = None

    def __repr__(self):
        return (
            f"Canvas("
            f"{self.width}x{self.height}, "
            f"dpi={self.dpi}, "
            f"background='{self.background}')"
        )
