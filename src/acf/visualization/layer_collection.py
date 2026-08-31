"""
Atmospheric Complexity Framework (ACF)

Layer Collection
"""

from acf.visualization.layer import Layer


class LayerCollection:
    """
    Ordered collection of scientific layers.
    """

    def __init__(self):

        self._layers = []

    ##################################################

    def add(self, layer: Layer):

        self._layers.append(layer)

        return layer

    ##################################################

    def remove(self, layer_id):

        self._layers = [layer for layer in self._layers if layer.id != layer_id]

    ##################################################

    def clear(self):

        self._layers.clear()

    ##################################################

    def get(self, layer_id):

        for layer in self._layers:
            if layer.id == layer_id:
                return layer

        return None

    ##################################################

    def by_name(self, name):

        for layer in self._layers:
            if layer.name == name:
                return layer

        return None

    ##################################################

    def visible(self):

        return [layer for layer in self._layers if layer.visible]

    ##################################################

    def hidden(self):

        return [layer for layer in self._layers if not layer.visible]

    ##################################################

    def names(self):

        return [layer.name for layer in self._layers]

    ##################################################

    def summary(self):

        return {
            "count": len(self._layers),
            "visible": len(self.visible()),
            "hidden": len(self.hidden()),
            "layers": self.names(),
        }

    ##################################################

    def __iter__(self):

        return iter(self._layers)

    ##################################################

    def __len__(self):

        return len(self._layers)

    ##################################################

    def __getitem__(self, index):

        return self._layers[index]
