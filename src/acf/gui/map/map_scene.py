"""
Atmospheric Complexity Framework (ACF)

Map Scene
=========

Scientific visualization scene controller.
"""

from PySide6.QtCore import QObject, Signal


class MapScene(QObject):
    """
    Central scene controller for map visualization.
    """

    sceneChanged = Signal()

    layerAdded = Signal(object)

    layerRemoved = Signal(str)

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.visualization_manager = None

        self.layers = []

        self.initialized = False

    ##################################################

    def initialize(self):

        if self.initialized:
            return

        self.initialized = True

        self.sceneChanged.emit()

    ##################################################

    def set_visualization_manager(
        self,
        manager,
    ):

        self.visualization_manager = manager

        self.refresh()

    ##################################################

    def add_layer(
        self,
        layer,
    ):

        if layer not in self.layers:
            self.layers.append(layer)

            self.layerAdded.emit(layer)

            self.sceneChanged.emit()

    ##################################################

    def remove_layer(
        self,
        layer_id,
    ):

        for layer in self.layers:
            if layer.id == layer_id:
                self.layers.remove(layer)

                self.layerRemoved.emit(layer_id)

                self.sceneChanged.emit()

                return

    ##################################################

    def clear(self):

        self.layers.clear()

        self.sceneChanged.emit()

    ##################################################

    def refresh(self):

        if self.visualization_manager is None:
            return

        manager = self.visualization_manager

        self.layers = manager.layer_manager.layers()

        self.sceneChanged.emit()

    ##################################################

    def render(self, axes):
        """
        Render all visible layers.

        NOTE: no rendering backend is wired up yet - this iterates
        visible layers but performs no draw call against `axes`
        (previously a silent no-op with only a "futur renderer system"
        comment; no caller or test currently depends on this method -
        verified). Left honestly incomplete rather than faked, per the
        per-layer renderer system planned for this scene controller.
        """

        for layer in self.layers:
            if not layer.visible:
                continue

            # futur renderer system: dispatch layer.render(axes) once a
            # concrete per-layer renderer backend is wired up here.

    ##################################################

    def status(self):

        return {
            "layers": len(self.layers),
            "visualization_manager": self.visualization_manager is not None,
            "initialized": self.initialized,
        }
