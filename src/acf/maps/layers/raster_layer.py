"""
Raster Layer
============

Couche raster utilisée pour afficher des champs météorologiques.
"""


class RasterLayer:
    """Représente une couche raster."""

    def __init__(self, name="", data=None, visible=True, opacity=1.0):
        self.name = name
        self.data = data
        self.visible = visible
        self.opacity = opacity

    def set_data(self, data):
        """Définit les données."""
        self.data = data

    def get_data(self):
        """Retourne les données."""
        return self.data

    def set_visible(self, visible):
        """Active ou désactive la couche."""
        self.visible = visible

    def is_visible(self):
        """Retourne l'état de visibilité."""
        return self.visible

    def set_opacity(self, opacity):
        """Définit l'opacité."""
        self.opacity = float(opacity)

    def clear(self):
        """Supprime les données."""
        self.data = None

    def __repr__(self):
        return (
            f"RasterLayer("
            f"name={self.name!r}, "
            f"visible={self.visible}, "
            f"opacity={self.opacity})"
        )
