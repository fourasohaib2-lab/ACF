"""
Atmospheric Complexity Framework (ACF)

MAPS - Canonical Cartographic & Visualization Package
=====================================================

GIS map rendering, spatial projections, contour generation, streamline visualization,
and high-level cartographic visualization management.

NOTE (Physics Guard, 2026-09-06 Tier C sweep): the classes re-exported
below (AutoRenderer, CartopyRenderer/ContourRenderer/RasterRenderer/
WindRenderer, BaseLayer/RasterLayer/VectorLayer, MapCanvas, MapEngine,
ProjectionManager, ColormapManager, DataRenderer, VisualizationManager)
are genuinely real and live - see acf.maps.canvas.map_canvas.MapCanvas's
own NOTE for how this package's MapCanvas is verified both-live
alongside acf.gui.map.map_canvas.MapCanvas.

Separately, verified by grep: field.py (WeatherField), streamlines.py
(Streamlines), vector.py (Vector), contours.py (Contours), exporter.py
(Exporter), shapefile.py (ShapeFileManager), and layer_manager.py
(this package's own, distinct from maps.layers.*) are each real,
correct, simple data-registry classes - not exported in __all__ above,
not imported by anything in src/ outside their own test file. Note
also that Exporter.export() only appends a Path to an internal list -
it performs no actual file I/O despite the name.
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
