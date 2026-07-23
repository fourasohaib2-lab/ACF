"""
Map Canvas
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from acf.maps.renderers.cartopy_renderer import CartopyRenderer
from acf.maps.renderers.raster_renderer import RasterRenderer
from acf.maps.renderers.contour_renderer import ContourRenderer
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
