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

NOTE (correction — real functional gaps, found during the
post-model4d audit, 2026-09-06): `draw_raster()`/`draw_contours()`
used to claim a truthy result with no real matplotlib drawing
primitive ever called (the canvas visually never changed), and
`draw_wind()` crashed immediately with a `TypeError` on any real call
(passed one `field` argument to `WindRenderer.set_field()`, which
needs `u` AND `v`) - reproduced directly before fixing. Zero real
callers or tests anywhere in the codebase exercised any of the three
(verified via grep) - real but previously-inert/unreachable gaps, not
a behavior change for any existing caller. See each method's own NOTE
for what was fixed (the crash) versus honestly disclosed (still no
real drawing primitive wired - would need real lon/lat coordinates
threaded through these methods' own signatures, a larger API change
than this pass makes).
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
        """
        NOTE (correction — real functional gap, found during the
        post-model4d audit, 2026-09-06): this only ever updated
        `self.raster_renderer`'s tracked field and returned whether a
        field was set (`RasterRenderer.render()`'s own `has_field()`
        check) - no real matplotlib drawing primitive
        (`pcolormesh`/`imshow`) was ever called and `self.draw()` was
        never invoked, so the canvas visually never changed despite
        claiming a truthy result. A real fix needs real longitude/
        latitude coordinate arrays threaded through this method's own
        signature (not present today - only a bare 2D `field`), a
        genuinely larger API change than fixing in place here. Zero
        real callers anywhere in the codebase depend on the previous
        (non-)rendering behavior (verified via grep, tests included) -
        a real but previously-inert gap, not a behavior change for any
        existing caller. Honestly disclosed instead of silently kept.
        """
        self.raster_renderer.set_field(field)
        field_set = self.raster_renderer.render()
        return {"field_set": field_set, "rendered": False, "status": "NOT_RENDERED_NO_REAL_DRAW_CALL_WIRED"}

    ##################################################

    def draw_contours(self, field):
        """Same real gap as draw_raster() - see its own NOTE. No real `contour()`/`contourf()` call is ever made here."""
        self.contour_renderer.set_field(field)
        field_set = self.contour_renderer.render()
        return {"field_set": field_set, "rendered": False, "status": "NOT_RENDERED_NO_REAL_DRAW_CALL_WIRED"}

    ##################################################

    def draw_wind(self, u, v):
        """
        Same real gap as draw_raster() - see its own NOTE. No real
        `quiver()`/`streamplot()` call is ever made here.

        NOTE (correction — reproducible crash, found during the
        post-model4d audit, 2026-09-06): this used to take a single
        `field` argument and pass it alone to
        `WindRenderer.set_field(u, v)`, which requires two - any real
        call (`draw_wind(some_array)`) raised `TypeError: set_field()
        missing 1 required positional argument: 'v'` immediately.
        Reproduced directly before fixing. Corrected to accept `u`/`v`
        separately, matching `WindRenderer.set_field()`'s real
        signature. Zero real callers anywhere in the codebase (verified
        via grep, tests included), so this was a real but previously-
        unreachable crash, not a behavior change for any existing caller.
        """
        self.wind_renderer.set_field(u, v)
        field_set = self.wind_renderer.has_field()
        return {"field_set": field_set, "rendered": False, "status": "NOT_RENDERED_NO_REAL_DRAW_CALL_WIRED"}


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

