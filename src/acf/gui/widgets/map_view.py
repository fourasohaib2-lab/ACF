"""
ACF Scientific Map View

Widget cartographique principal.

NOTE (correction — wrong CartopyRenderer, name collision): this
imported acf.maps.CartopyRenderer (re-exported from
acf.maps.renderers.cartopy_renderer), whose __init__ requires a real
GUI canvas object with no default and which has no create_map()/
status() methods - not what this widget calls. MapView() crashed
immediately on construction (TypeError: missing 1 required positional
argument: 'canvas'), which meant DashboardLayout.build() - and so
DashboardManager.initialize(), the real GUI dashboard's setup path -
crashed too, with zero test coverage anywhere in this chain (same
bug family, and the same fix, as acf/maps/data_renderer.py's own
NOTE (correction) - see that module for the full explanation of which
CartopyRenderer is the right one and why).
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from acf.visualization.cartopy_renderer import CartopyRenderer


class MapView(QWidget):
    """
    Carte scientifique interactive ACF.
    """

    def __init__(self):

        super().__init__()

        self.renderer = CartopyRenderer()

        self.canvas = None

        self.build()

    ##################################################

    def build(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        figure, axis = self.renderer.create_map()

        self.canvas = FigureCanvasQTAgg(figure)

        layout.addWidget(self.canvas)

    ##################################################

    def clear(self):

        self.renderer.clear()

    ##################################################

    def refresh(self):

        if self.canvas:
            self.canvas.draw()

    ##################################################

    def status(self):

        return {"widget": "MapView", "renderer": self.renderer.status()}
