"""
Atmospheric Complexity Framework (ACF)

Visualization Manager
"""

from acf.maps.auto_renderer import AutoRenderer
from acf.maps.layer_manager import LayerManager


class VisualizationManager:
    """
    Central manager for scientific visualization.
    """

    def __init__(self):
        self.layer_manager = LayerManager()
        self.renderer = AutoRenderer()
        self.current_dataset = None
        self.current_layer = None
        self.initialized = False

    def initialize(self):
        if self.initialized:
            return
        self.renderer.initialize()
        self.initialized = True

    def load_dataset(self, dataset):
        self.current_dataset = dataset

    def dataset(self):
        return self.current_dataset

    def layers(self):
        return self.layer_manager

    def render(self, family, longitude, latitude, values):
        if self.current_dataset is None:
            raise RuntimeError("No dataset loaded.")

        variable = self.renderer.render_dataset(
            self.current_dataset,
            family,
            longitude,
            latitude,
            values,
        )

        layer = self.layer_manager.create_layer(
            name=family,
            variable=variable,
        )

        self.current_layer = layer
        return layer

    def remove_layer(self, layer_id):
        self.layer_manager.remove_layer(layer_id)

    def clear(self):
        self.layer_manager.clear()
        self.current_dataset = None
        self.current_layer = None

    def status(self):
        return {
            "initialized": self.initialized,
            "dataset": (self.current_dataset.name if self.current_dataset else None),
            "current_layer": (self.current_layer.name if self.current_layer else None),
            "layer_manager": self.layer_manager.status(),
            "renderer": self.renderer.status(),
        }
