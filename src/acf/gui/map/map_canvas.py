"""
Atmospheric Complexity Framework (ACF)

MapCanvas Pro
=============

Professional Map Engine
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
)

import cartopy.crs as ccrs

from .map_navigation import NavigationMixin
from .map_rendering import RenderingMixin
from .map_events import EventMixin
from .map_status import StatusMixin
from .map_export import ExportMixin

from .map_scene import MapScene
from .map_camera import MapCamera

from .projections.projection_manager import (
    ProjectionManager,
)

from .rendering.renderer_manager import (
    RendererManager,
)
from .renderers.world_renderer import WorldRenderer


class MapCanvas(
    QWidget,
    NavigationMixin,
    RenderingMixin,
    EventMixin,
    StatusMixin,
    ExportMixin,
):
    """
    Professional Map Canvas.

    Central graphical engine of ACF.
    """

    ##################################################

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):

        super().__init__(parent)

        ##################################################
        # Core
        ##################################################

        self.scene = None

        self.camera = None

        self.projection_manager = None

        self.renderer_manager = None

        
        self.world_renderer = None

        
        ##################################################
        # Matplotlib
        ##################################################

        self.figure = None

        self.axes = None

        self.canvas = None

        self.projection = None

        ##################################################

        self._initialized = False

        self.initialize()

    ##################################################

    def initialize(self):
        """
        Initialize Map Engine.
        """

        ##################################################
        # Managers
        ##################################################

        self.scene = MapScene(self)

        self.camera = MapCamera(self)

        self.projection_manager = ProjectionManager(self)

        self.renderer_manager = RendererManager(self)

        self.world_renderer = WorldRenderer()
        self.scene = MapScene(self)
        self.camera = MapCamera(self)
        self.projection_manager = ProjectionManager(self)
        self.renderer_manager = RendererManager(self)        
        ##################################################
        # Projection
        ##################################################

        self.projection = ccrs.PlateCarree()

        ##################################################
        # Figure
        ##################################################

        self.figure = plt.figure(
            figsize=(12, 8)
        )

        ##################################################
        # Axes
        ##################################################

        self.axes = self.figure.add_subplot(
            111,
            projection=self.projection,
        )

        ##################################################
        # Canvas
        ##################################################

        self.canvas = FigureCanvas(
            self.figure
        )

        ##################################################
        # Layout
        ##################################################

        layout = QVBoxLayout()

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.addWidget(
            self.canvas
        )

        self.setLayout(
            layout
        )

        ##################################################
        # Initial Draw
        ##################################################

        self.canvas.draw()
        self._initialized = True

        ##################################################

        self._initialized = True

    ##################################################

    def refresh(self):
        """
        Refresh canvas.
        """

        if self.canvas is not None:

            self.canvas.draw_idle()

    ##################################################

    def clear(self):

        if self.axes is None:
            return

        self.axes.clear()

        self.refresh()

    ##################################################

    def draw_world(self):
        """
        Draw professional world map.
        """

        if self.axes is None:
            return

        self.axes.clear()

        self.world_renderer.render(self.axes)

        self.canvas.draw_idle()

    ##################################################

    def status(self):

        return {

            "initialized": self._initialized,

            "scene": self.scene is not None,

            "camera": self.camera is not None,

            "projection_manager": self.projection_manager is not None,

            "renderer_manager": self.renderer_manager is not None,

            "figure": self.figure is not None,

            "axes": self.axes is not None,

            "canvas": self.canvas is not None,

            "projection": type(self.projection).__name__
            if self.projection else None,

        }

    ##################################################

    def closeEvent(self, event):

        if self.figure is not None:
            plt.close(self.figure)

        super().closeEvent(event)

