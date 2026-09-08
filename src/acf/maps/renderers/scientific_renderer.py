"""
ACF Scientific Renderer Engine

Transformation des données météo en couches graphiques.
"""

from acf.maps.layers.base_layer import BaseLayer as Layer
from acf.maps.styles.colormap_manager import ColormapManager as ColorMapManager
from acf.visualization.colormap import ColorMapManager as _MeteorologicalColormapDefaults


class ScientificRenderer:
    """
    Moteur principal de rendu scientifique ACF.
    """

    def __init__(self):
        self.colormaps = ColorMapManager()
        # NOTE (correction): ColorMapManager (maps.styles.colormap_manager)
        # is a generic empty registry by design (same convention as
        # StandardsManager/CatalogManager elsewhere - it starts empty and
        # expects the caller to populate it) - but this class never did,
        # so every get_colormap() lookup below for temperature/wind/
        # pressure/humidity silently returned None instead of a usable
        # colormap name, while every OTHER, unmatched variable name fell
        # through to the "viridis" default - an inverted outcome where
        # the 4 explicitly-supported meteorological categories were
        # worse off than an unrecognized one. Seeded here from
        # acf.visualization.colormap.ColorMapManager.DEFAULT_MAPS (the
        # one existing place ACF's real default meteorological palette
        # assignments - temperature/pressure/wind/humidity/etc. - are
        # already recorded) rather than duplicating those values here.
        for name, cmap in _MeteorologicalColormapDefaults.DEFAULT_MAPS.items():
            self.colormaps.add(name, cmap)
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
            return self.colormaps.get("temperature") or "viridis"
        if "wind" in variable:
            return self.colormaps.get("wind") or "viridis"
        if "pressure" in variable:
            return self.colormaps.get("pressure") or "viridis"
        if "humidity" in variable:
            return self.colormaps.get("humidity") or "viridis"
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
