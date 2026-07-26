"""
Atmospheric Complexity Framework (ACF)

Layer Manager
=============

Professional management of map layers.
"""

from PySide6.QtCore import QObject, Signal


class LayerManager(QObject):
    """
    Central manager of all map layers.
    """

    layerAdded = Signal(object)
    layerRemoved = Signal(str)
    layerChanged = Signal()
    orderChanged = Signal()

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self._layers = []

    ##################################################

    def add_layer(self, layer):
        """
        Add a layer.
        """

        self._layers.append(layer)

        self.layerAdded.emit(layer)

        self.layerChanged.emit()

    ##################################################

    def remove_layer(self, layer_id):
        """
        Remove a layer by id.
        """

        for layer in self._layers:

            if layer.id == layer_id:

                self._layers.remove(layer)

                self.layerRemoved.emit(layer_id)

                self.layerChanged.emit()

                return True

        return False

    ##################################################

    def layer(self, layer_id):
        """
        Return one layer.
        """

        for layer in self._layers:

            if layer.id == layer_id:
                return layer

        return None

    ##################################################

    def layers(self):
        """
        Return all layers.
        """

        return list(self._layers)

    ##################################################

    def visible_layers(self):
        """
        Return only visible layers.
        """

        return [
            layer
            for layer in self._layers
            if layer.visible
        ]

    ##################################################

    def clear(self):
        """
        Remove every layer.
        """

        self._layers.clear()

        self.layerChanged.emit()

    ##################################################

    def move_up(self, layer_id):
        """
        Move one layer upward.
        """

        for i, layer in enumerate(self._layers):

            if layer.id == layer_id and i < len(self._layers) - 1:

                self._layers[i], self._layers[i + 1] = (
                    self._layers[i + 1],
                    self._layers[i],
                )

                self.orderChanged.emit()

                return

    ##################################################

    def move_down(self, layer_id):
        """
        Move one layer downward.
        """

        for i, layer in enumerate(self._layers):

            if layer.id == layer_id and i > 0:

                self._layers[i], self._layers[i - 1] = (
                    self._layers[i - 1],
                    self._layers[i],
                )

                self.orderChanged.emit()

                return

    ##################################################

    def status(self):

        return {

            "layers": len(self._layers),

            "visible": len(self.visible_layers()),

            "names": [
                layer.name
                for layer in self._layers
            ],

        }

