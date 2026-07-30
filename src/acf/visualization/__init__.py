"""
Atmospheric Complexity Framework (ACF)

VISUALIZATION - Backward Compatibility Facade Layer
===================================================

This package provides 100% backward compatibility for legacy imports by redirecting
to the canonical `acf.maps` cartographic package using PEP 562 dynamic attributes.
"""

import importlib

__all__ = [
    "MapEngine",
    "LayerManager",
    "MapCanvas",
    "CartopyRenderer",
    "RasterRenderer",
    "ContourRenderer",
    "WindRenderer",
    "BaseLayer",
    "RasterLayer",
    "VectorLayer",
    "ProjectionManager",
    "ColormapManager",
    "VisualizationManager",
    "AutoRenderer",
    "DataRenderer",
    "Layer",
    "LayerCollection",
    "LayerGroup",
    "ScientificRenderer",
    "ColorMapManager",
]

_MAPS_MAPPINGS = {
    "MapEngine": ("acf.maps.map_engine", "MapEngine"),
    "LayerManager": ("acf.maps.layer_manager", "LayerManager"),
    "MapCanvas": ("acf.maps.canvas.map_canvas", "MapCanvas"),
    "CartopyRenderer": ("acf.maps.renderers.cartopy_renderer", "CartopyRenderer"),
    "RasterRenderer": ("acf.maps.renderers.raster_renderer", "RasterRenderer"),
    "ContourRenderer": ("acf.maps.renderers.contour_renderer", "ContourRenderer"),
    "WindRenderer": ("acf.maps.renderers.wind_renderer", "WindRenderer"),
    "BaseLayer": ("acf.maps.layers.base_layer", "BaseLayer"),
    "RasterLayer": ("acf.maps.layers.raster_layer", "RasterLayer"),
    "VectorLayer": ("acf.maps.layers.vector_layer", "VectorLayer"),
    "ProjectionManager": ("acf.maps.projections.projection_manager", "ProjectionManager"),
    "ColormapManager": ("acf.maps.styles.colormap_manager", "ColormapManager"),
    "VisualizationManager": ("acf.maps.visualization_manager", "VisualizationManager"),
    "AutoRenderer": ("acf.maps.auto_renderer", "AutoRenderer"),
    "DataRenderer": ("acf.maps.data_renderer", "DataRenderer"),
}

_VIZ_MAPPINGS = {
    "Layer": ("acf.visualization.layer", "Layer"),
    "LayerCollection": ("acf.visualization.layer_collection", "LayerCollection"),
    "LayerGroup": ("acf.visualization.layer_group", "LayerGroup"),
    "ScientificRenderer": ("acf.visualization.renderer", "ScientificRenderer"),
    "ColorMapManager": ("acf.visualization.colormap", "ColorMapManager"),
}


def __getattr__(name):
    if name in _MAPS_MAPPINGS:
        mod_path, attr = _MAPS_MAPPINGS[name]
        mod = importlib.import_module(mod_path)
        return getattr(mod, attr)
    if name in _VIZ_MAPPINGS:
        mod_path, attr = _VIZ_MAPPINGS[name]
        mod = importlib.import_module(mod_path)
        return getattr(mod, attr)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
