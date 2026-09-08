"""
ACF Visualization Layer System

Gestion des couches scientifiques.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class Layer:
    """
    Représente une couche de visualisation scientifique.
    """

    def __init__(
        self,
        name: str,
        variable: str = "",
        dataset=None,
        visible: bool = True,
    ):

        self.id = str(uuid4())

        self.name = name

        self.variable = variable

        self.dataset = dataset

        self.visible = visible

        self.opacity = 1.0

        self.created = datetime.now(timezone.utc).isoformat()

        # Paramètres graphiques

        self.colormap = "viridis"

        self.level = None

        self.style: dict[str, Any] = {}

    ##################################################

    def show(self):

        self.visible = True

    def hide(self):

        self.visible = False

    def toggle(self):

        self.visible = not self.visible

    ##################################################

    def set_opacity(self, value: float):

        self.opacity = max(0.0, min(1.0, value))

    ##################################################

    def set_colormap(self, cmap: str):

        self.colormap = cmap

    ##################################################

    def summary(self):

        return {
            "id": self.id,
            "name": self.name,
            "variable": self.variable,
            "visible": self.visible,
            "opacity": self.opacity,
            "colormap": self.colormap,
            "level": self.level,
        }

    def __repr__(self):

        return f"Layer(name='{self.name}', variable='{self.variable}', visible={self.visible})"
