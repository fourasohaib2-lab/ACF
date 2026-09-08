"""
Base Layer

NOTE (correction): __init__ only accepted `name`, but
ScientificRenderer.create_layer() (maps/renderers/scientific_renderer.py)
constructs this class as Layer(name=name, variable=variable) - every
call crashed with "TypeError: BaseLayer.__init__() got an unexpected
keyword argument 'variable'" (confirmed: VisualizationManager.render(),
the maps/ visualization pipeline's real entry point, crashed here
with zero test coverage anywhere in this chain to catch it). Several
callers (ScientificRenderer.render_info(), DataRenderer.status()) also
already read a `.variable` attribute off layer objects via getattr(),
confirming this was meant to be a real constructor parameter, not a
typo to remove.
"""


class BaseLayer:
    def __init__(self, name, variable=None):

        self.name = name
        self.variable = variable
        self.visible = True
        self.opacity = 1.0

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_opacity(self, value):

        value = float(value)

        value = max(value, 0)

        value = min(value, 1)

        self.opacity = value
