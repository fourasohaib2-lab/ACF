"""
Atmospheric Complexity Framework (ACF)

Layer Group
"""

from acf.visualization.layer_collection import LayerCollection


class LayerGroup:
    """
    Group of visualization layers.
    """

    def __init__(self, name):

        self.name = name

        self.visible = True

        self.layers = LayerCollection()

        self.groups = []

    ##################################################

    def add_layer(self, layer):

        return self.layers.add(layer)

    ##################################################

    def remove_layer(self, layer_id):

        self.layers.remove(layer_id)

    ##################################################

    def add_group(self, group):

        self.groups.append(group)

        return group

    ##################################################

    def remove_group(self, name):

        self.groups = [group for group in self.groups if group.name != name]

    ##################################################

    def get_group(self, name):

        for group in self.groups:
            if group.name == name:
                return group

        return None

    ##################################################

    def show(self):

        self.visible = True

        for layer in self.layers:
            layer.visible = True

        for group in self.groups:
            group.show()

    ##################################################

    def hide(self):

        self.visible = False

        for layer in self.layers:
            layer.visible = False

        for group in self.groups:
            group.hide()

    ##################################################

    def summary(self):

        return {
            "name": self.name,
            "visible": self.visible,
            "layers": self.layers.summary(),
            "groups": [group.name for group in self.groups],
        }

    ##################################################

    def __len__(self):

        return len(self.layers)

    ##################################################

    def __repr__(self):

        return f"LayerGroup(name='{self.name}', layers={len(self.layers)}, groups={len(self.groups)})"
