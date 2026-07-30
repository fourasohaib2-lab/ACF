"""
ACF Scientific Renderer Engine

Transformation des données météo en couches graphiques.
"""

from acf.maps.layers.base_layer import BaseLayer as Layer
from acf.maps.styles.colormap_manager import ColormapManager as ColorMapManager


class ScientificRenderer:
    """
    Moteur principal de rendu scientifique ACF.
    """

    def __init__(self):
        self.colormaps = ColorMapManager()
        self.layers = []

    def create_layer(self, dataset, variable, name=None):
        if name is None:
            name = variable

        layer = Layer(name=name, variable=variable)
        self.layers.append(layer)
        return layer

    def get_colormap(self, variable):
        variable = str(variable).lower()

        if "temp" in variable:
            return self.colormaps.get("temperature")
        if "wind" in variable:
            return self.colormaps.get("wind")
        if "pressure" in variable:
            return self.colormaps.get("pressure")
        if "humidity" in variable:
            return self.colormaps.get("humidity")
        return "viridis"

    def render_info(self, layer):
        return {
            "layer": getattr(layer, "name", str(layer)),
            "variable": getattr(layer, "variable", str(layer)),
            "colormap": self.get_colormap(getattr(layer, "variable", "")),
        }

    def status(self):
        return {
            "layers": len(self.layers),
            "engine": "ACF Scientific Renderer",
        }
