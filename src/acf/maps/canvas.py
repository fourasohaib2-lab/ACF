"""
Atmospheric Complexity Framework (ACF)
Canvas
=====================================

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): this
module is dead code. `src/acf/maps/canvas/` is ALSO a package with its
own __init__.py, which Python's import resolution always finds before
this sibling module.py of the same name - so `import acf.maps.canvas`
can never actually reach this file (confirmed empirically:
`inspect.getfile()` after that import resolves to
maps/canvas/__init__.py). The package's own Canvas class (in
maps/canvas/map_canvas.py) carries the identical docstring as the
Canvas class below, confirming this file is a stale leftover duplicate
rather than uniquely-valuable trapped code - the real, reachable
Canvas/MapCanvas are the package's versions. Not deleted per project
convention - flagged so nobody mistakes this for live code. Same
situation as data/engine.py's NOTE. (The `from .map_canvas import
MapCanvas` line below would itself fail if this file were ever somehow
imported directly, since there is no sibling map_canvas.py next to
this file - one more sign this was never actually exercised.)
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
        return f"Canvas({self.width}x{self.height}, dpi={self.dpi}, background='{self.background}')"
