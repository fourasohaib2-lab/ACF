"""
Atmospheric Complexity Framework (ACF)

Renderer Manager
================

Central rendering engine.
"""

from PySide6.QtCore import QObject, Signal


class RendererManager(QObject):
    """
    Central renderer manager.

    Coordinates all scientific renderers.
    """

    ##################################################

    rendererAdded = Signal(str)

    rendererRemoved = Signal(str)

    renderingStarted = Signal()

    renderingFinished = Signal()

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.initialize()
    ##################################################

    def initialize(self):
        """
        Initialize renderer manager.
        """

        self._renderers = {}

        self._default_renderer = None
    ##################################################

    def register_renderer(
        self,
        name,
        renderer,
    ):
        """
        Register a renderer.
        """

        self._renderers[name] = renderer

        if self._default_renderer is None:
            self._default_renderer = name

        self.rendererAdded.emit(name)

    ##################################################

    def unregister_renderer(
        self,
        name,
    ):
        """
        Remove a renderer.
        """

        if name not in self._renderers:
            return

        del self._renderers[name]

        self.rendererRemoved.emit(name)
    ##################################################

    def renderer(self, name):

        return self._renderers.get(name)

    ##################################################

    def renderers(self):

        return dict(self._renderers)

    ##################################################

    def renderer_names(self):

        return sorted(self._renderers.keys())
    ##################################################

    def status(self):

        return {

            "count": len(self._renderers),

            "default": self._default_renderer,

            "renderers": self.renderer_names(),

        }

