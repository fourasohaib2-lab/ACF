"""
Atmospheric Complexity Framework (ACF)

Layer Manager
"""

from PySide6.QtCore import QObject, Signal

from acf.visualization.layer import Layer


class LayerManager(QObject):
    """
    Manage scientific visualization layers.
    """

    layerAdded = Signal(object)

    layerRemoved = Signal(str)

    layerChanged = Signal(object)

    layersCleared = Signal()

    layerMoved = Signal()

    currentLayerChanged = Signal(object)

    ##################################################

    def __init__(self):

        super().__init__()

        self._layers = []

        self._current_layer = None

    ##################################################

    def add_layer(
        self,
        layer: Layer,
    ):

        self._layers.append(layer)

        self.layerAdded.emit(layer)

        if self._current_layer is None:
            self._current_layer = layer

            self.currentLayerChanged.emit(layer)

        return layer

    ##################################################

    def create_layer(
        self,
        name,
        variable,
        **kwargs,
    ):

        layer = Layer(
            name=name,
            variable=variable,
            **kwargs,
        )

        return self.add_layer(layer)

    ##################################################

    def remove_layer(
        self,
        layer_id,
    ):

        layer = self.get_layer(layer_id)

        if layer is None:
            return

        self._layers.remove(layer)

        self.layerRemoved.emit(layer_id)

        if self._current_layer == layer:
            if self._layers:
                self._current_layer = self._layers[-1]

            else:
                self._current_layer = None

            self.currentLayerChanged.emit(self._current_layer)

    ##################################################

    def clear(self):

        self._layers.clear()

        self._current_layer = None

        self.layersCleared.emit()

        self.currentLayerChanged.emit(None)

    ##################################################

    def get_layer(
        self,
        layer_id,
    ):

        for layer in self._layers:
            if layer.id == layer_id:
                return layer

        return None

    ##################################################

    def get_layer_by_name(
        self,
        name,
    ):

        for layer in self._layers:
            if layer.name == name:
                return layer

        return None

    ##################################################

    def set_current_layer(
        self,
        layer_id,
    ):

        layer = self.get_layer(layer_id)

        if layer is None:
            return

        if self._current_layer == layer:
            return

        self._current_layer = layer

        self.currentLayerChanged.emit(layer)

    ##################################################

    def current_layer(self):

        return self._current_layer

    ##################################################

    def current_layer_id(self):

        if self._current_layer is None:
            return None

        return self._current_layer.id

    ##################################################

    def layers(self):

        return list(self._layers)

    ##################################################

    def visible_layers(self):

        return [layer for layer in self._layers if layer.visible]

    ##################################################

    def show_layer(
        self,
        layer_id,
    ):

        layer = self.get_layer(layer_id)

        if layer is None:
            return

        if not layer.visible:
            layer.visible = True

            self.layerChanged.emit(layer)

    ##################################################

    def hide_layer(
        self,
        layer_id,
    ):

        layer = self.get_layer(layer_id)

        if layer is None:
            return

        if layer.visible:
            layer.visible = False

            self.layerChanged.emit(layer)

    ##################################################

    def move_layer(
        self,
        old_index,
        new_index,
    ):

        if old_index < 0 or old_index >= len(self._layers):
            return

        if new_index < 0 or new_index >= len(self._layers):
            return

        layer = self._layers.pop(old_index)

        self._layers.insert(
            new_index,
            layer,
        )

        self.layerMoved.emit()

    ##################################################

    def count(self):

        return len(self._layers)

    ##################################################

    def status(self):

        return {
            "layers": self.count(),
            "visible": len(self.visible_layers()),
            "current_layer": self._current_layer.name if self._current_layer else None,
            "names": [layer.name for layer in self._layers],
        }
