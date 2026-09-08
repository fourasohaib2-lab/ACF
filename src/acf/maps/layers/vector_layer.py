"""
Vector Layer
============

Gestion d'une couche vectorielle.
"""

from .base_layer import BaseLayer


class VectorLayer(BaseLayer):
    def __init__(self, name="Vector Layer"):
        super().__init__(name)

        self.features = []

    def add_feature(self, feature):
        self.features.append(feature)

    def remove_feature(self, feature):
        if feature in self.features:
            self.features.remove(feature)

    def get_features(self):
        return self.features

    def count(self):
        return len(self.features)

    def clear(self):
        self.features.clear()

    def __repr__(self):
        return f"VectorLayer(name='{self.name}', features={len(self.features)})"
