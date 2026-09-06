"""
Atmospheric Complexity Framework (ACF)

VISUALIZATION - Backward Compatibility Facade Layer
===================================================

This package provides 100% backward compatibility for legacy imports by redirecting
to the canonical `acf.maps` cartographic package using PEP 562 dynamic attributes,
while exporting the new AWCI 2D/3D/4D visualization workstation engine.

AUDIT NOTE (2026-09-06, Tier C sweep): builds on 5419a58's large sample
of this package (root shims verified forwarding to acf.maps;
ai_forecast_center/, layer_engine/, gpu/gpu_backend.py, widgets/
awci_dashboard.py already carrying their own honest disclosures -
layer_permissions.py's always-True check_layer_access() correctly left
as a judgment call, no auth system exists in this single-operator app
to define a real policy against). This pass independently re-verified
that finding (no generic docstring-bloat template found anywhere in
this package - 0 hits) and read the remaining ~20 not specifically
named files (volume_engine/, camera/, scene/, timeline/, legends/,
layers/scientific_layers.py, layer.py/layer_group.py/
layer_collection.py/colormap.py) - all genuinely honest: real,
correctly-scoped metadata/config/cache classes, no fabricated
computation. Nothing new to disclose.
"""

import importlib

__all__ = [
    "AWCIDashboardEngine",
    "AutoRenderer",
    "BaseLayer",
    "CameraController",
    "CartopyRenderer",
    "ColorMapManager",
    "ColorTableRegistry",
    "ColormapManager",
    "ContourRenderer",
    "DataRenderer",
    "GPUBackend",
    "IsosurfaceLayer",
    "Layer",
    "LayerCollection",
    "LayerGroup",
    "LayerManager",
    "MapCanvas",
    "MapEngine",
    "ParticleFlowLayer",
    "ProjectionManager",
    "RadarVolumeLayer",
    "RasterLayer",
    "RasterRenderer",
    "SatelliteRGBLayer",
    "ScientificRenderer",
    "TimelineController",
    "VectorLayer",
    "VisualizationManager",
    "VisualizationScene",
    "WindRenderer",
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
    "VisualizationScene": ("acf.visualization.scene.scene_manager", "VisualizationScene"),
    "CameraController": ("acf.visualization.camera.camera_controller", "CameraController"),
    "ParticleFlowLayer": ("acf.visualization.layers.scientific_layers", "ParticleFlowLayer"),
    "IsosurfaceLayer": ("acf.visualization.layers.scientific_layers", "IsosurfaceLayer"),
    "RadarVolumeLayer": ("acf.visualization.layers.scientific_layers", "RadarVolumeLayer"),
    "SatelliteRGBLayer": ("acf.visualization.layers.scientific_layers", "SatelliteRGBLayer"),
    "TimelineController": ("acf.visualization.timeline.timeline_controller", "TimelineController"),
    "ColorTableRegistry": ("acf.visualization.legends.color_tables", "ColorTableRegistry"),
    "GPUBackend": ("acf.visualization.gpu.gpu_backend", "GPUBackend"),
    "AWCIDashboardEngine": ("acf.visualization.widgets.awci_dashboard", "AWCIDashboardEngine"),
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
