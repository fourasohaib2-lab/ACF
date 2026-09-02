"""
Map Canvas

NOTE (found while auditing docs/architecture/duplicate_components.md's
"Canvas carte" row, NOT changed — RÈGLE D'OR / single source of truth):
this `MapCanvas` and `acf.gui.map.map_canvas.MapCanvas` are a genuine,
verified-both-live duplicate - unlike this session's other X.py-vs-X/
findings (data/engine.py, model4d/operators.py, maps/canvas.py, this
same package's gui.map/projections/layers/renderers subpackages), there
is no import-resolution collision silently picking one: both are
independently importable, and both have real, distinct consumers today
(confirmed by grep, not assumed).

This class (`acf.maps.canvas.map_canvas.MapCanvas`) is a direct
`FigureCanvasQTAgg` subclass, wiring its own `CartopyRenderer`/
`RasterRenderer`/`ContourRenderer`/`WindRenderer` internally. It is the
one re-exported by `acf.maps` (this package's own docstring calls
itself the "Canonical Cartographic & Visualization Package") and by
`acf.visualization`'s lazy re-export table, and is what
`tests/test_cartopy_renderer.py` exercises.

`acf.gui.map.map_canvas.MapCanvas` is a `QWidget` wrapping a
`MapProjection`/`MapRenderer`/`LayerManager` trio (the flat
`gui/map/map_*.py` files - themselves already documented in
`gui/map/__init__.py`'s own NOTE as the ones genuinely used by the real
app). It is the one actually embedded in ESOC's live window
(`acf.gui.esoc.view_manager.ViewManager` and
`acf.gui.main_window.main_window.MainWindow` both import it directly),
despite `acf.maps` branding itself "Canonical" in its module docstring
above.

Consolidating these for real - per this repository's own
`docs/architecture/duplicate_components.md` plan ("tests de
non-régression avant toute migration") - would mean picking a winner
and migrating either ESOC's real running GUI or `acf.maps`/
`acf.visualization`'s public API onto the other's shape
(this class IS a matplotlib canvas you call `.draw()`/`.figure` on
directly, while the other is a composite `QWidget` that merely embeds
one via a layout - not drop-in compatible shapes), which is
a real, scoped design decision this pass does not make unilaterally.
Not deleted or merged per project convention - flagged so the "Canonical"
docstring above isn't mistaken for meaning this is the one live GUI
consumers actually use.
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from acf.maps.renderers.cartopy_renderer import CartopyRenderer
from acf.maps.renderers.contour_renderer import ContourRenderer
from acf.maps.renderers.raster_renderer import RasterRenderer
from acf.maps.renderers.wind_renderer import WindRenderer


class MapCanvas(FigureCanvasQTAgg):
    def __init__(self):

        self.figure = Figure(figsize=(12, 8))

        super().__init__(self.figure)

        # Axe Matplotlib par défaut
        self.axes = self.figure.add_subplot(111)

        self.renderer = CartopyRenderer(self)
        self.raster_renderer = RasterRenderer()
        self.contour_renderer = ContourRenderer()
        self.wind_renderer = WindRenderer()

        self.initialize()

    ##################################################

    def initialize(self):

        self.axes.set_title("Atmospheric Complexity Framework")

        self.axes.set_xlabel("Longitude")

        self.axes.set_ylabel("Latitude")

        self.axes.grid(True)

        self.draw()

    ##################################################

    def clear_canvas(self):

        self.figure.clear()

        self.axes = self.figure.add_subplot(111)

        self.initialize()

    ##################################################

    def plot_demo(self):

        self.axes.clear()

        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16]

        self.axes.plot(x, y)

        self.axes.set_title("Demo Plot")

        self.draw()

    ##################################################

    def draw_world(self):

        self.renderer.draw_world()

    ##################################################

    def draw_raster(self, field):

        self.raster_renderer.set_field(field)

        return self.raster_renderer.render()

    ##################################################

    def draw_contours(self, field):

        self.contour_renderer.set_field(field)

        return self.contour_renderer.render()

    ##################################################

    def draw_wind(self, field):

        self.wind_renderer.set_field(field)

        return self.wind_renderer.render()


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

