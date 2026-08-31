"""
Atmospheric Complexity Framework (ACF)

MAPS - Canonical Cartographic & Visualization Package
=====================================================

GIS map rendering, spatial projections, contour generation, streamline visualization,
and high-level cartographic visualization management.
"""

from acf.maps.auto_renderer import AutoRenderer
from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.data_renderer import DataRenderer
from acf.maps.layer_manager import LayerManager
from acf.maps.layers.base_layer import BaseLayer
from acf.maps.layers.raster_layer import RasterLayer
from acf.maps.layers.vector_layer import VectorLayer
from acf.maps.map_engine import MapEngine
from acf.maps.projections.projection_manager import ProjectionManager
from acf.maps.renderers.cartopy_renderer import CartopyRenderer
from acf.maps.renderers.contour_renderer import ContourRenderer
from acf.maps.renderers.raster_renderer import RasterRenderer
from acf.maps.renderers.wind_renderer import WindRenderer
from acf.maps.styles.colormap_manager import ColormapManager
from acf.maps.visualization_manager import VisualizationManager

__all__ = [
    "AutoRenderer",
    "BaseLayer",
    "CartopyRenderer",
    "ColormapManager",
    "ContourRenderer",
    "DataRenderer",
    "LayerManager",
    "MapCanvas",
    "MapEngine",
    "ProjectionManager",
    "RasterLayer",
    "RasterRenderer",
    "VectorLayer",
    "VisualizationManager",
    "WindRenderer",
]
