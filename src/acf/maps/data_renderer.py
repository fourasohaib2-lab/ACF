"""
ACF Meteorological Data Renderer

Connexion entre:
- Dataset
- Layer
- ScientificRenderer
- CartopyRenderer

NOTE (correction — wrong CartopyRenderer, name collision): this
imported acf.maps.renderers.cartopy_renderer.CartopyRenderer, whose
__init__ requires a real GUI canvas object (no default) and which has
no create_map()/add_field()/status() methods - not what this class
calls at all. DataRenderer() crashed immediately on construction
(TypeError: missing 1 required positional argument: 'canvas'), and
VisualizationManager() (maps/visualization_manager.py), which
constructs a DataRenderer via AutoRenderer at __init__ time, crashed
the same way - the entire maps/ visualization pipeline's central
manager could not be instantiated at all, with zero test coverage
anywhere to catch it. The class this module actually needs -
optional canvas, and the legacy create_map()/add_field()/status()
methods this class calls - is
acf.visualization.cartopy_renderer.CartopyRenderer, a compatibility
facade explicitly built for exactly this headless/canvas-less usage.

The import of that facade is deliberately deferred to __init__ rather
than done at module level: acf.visualization.cartopy_renderer itself
imports from acf.maps.renderers.cartopy_renderer, which - because
Python always initializes a parent package before any of its
submodules - forces acf/maps/__init__.py to run first; that __init__
eagerly imports this very module (via auto_renderer.py). A
module-level import here is therefore circular whenever something
outside acf.maps imports acf.visualization.cartopy_renderer first
(e.g. acf.gui.widgets.map_view - confirmed reproducing "ImportError:
cannot import name 'CartopyRenderer' from partially initialized
module"). Deferring the import to call time (when both modules are
already fully initialized either way) sidesteps the cycle without
restructuring either package.
"""

from acf.maps.renderers.scientific_renderer import ScientificRenderer


class DataRenderer:
    """
    Renderer des données météorologiques ACF.
    """

    def __init__(self):
        from acf.visualization.cartopy_renderer import CartopyRenderer

        self.scientific = ScientificRenderer()
        self.cartopy = CartopyRenderer()
        self.current_layer = None

    def initialize_map(self):
        return self.cartopy.create_map()

    def find_variable(self, dataset, variable):
        if dataset.has_variable(variable):
            return variable
        for name in dataset.variable_names:
            if variable.lower() in name.lower():
                return name
        return None

    def create_layer(self, dataset, variable):
        real_variable = self.find_variable(dataset, variable)
        if real_variable is None:
            raise ValueError(f"Variable '{variable}' not found")
        layer = self.scientific.create_layer(dataset, real_variable, real_variable)
        self.current_layer = layer
        return layer

    def get_colormap(self, variable):
        return self.scientific.get_colormap(variable)

    def render(self, longitude, latitude, data, variable):
        cmap = self.get_colormap(variable)
        layer = self.cartopy.add_field(longitude, latitude, data, colormap=cmap)
        return layer

    def status(self):
        return {
            "scientific": self.scientific.status(),
            "cartopy": self.cartopy.status(),
            "current_layer": (self.current_layer.summary() if hasattr(self.current_layer, "summary") else None),
        }
