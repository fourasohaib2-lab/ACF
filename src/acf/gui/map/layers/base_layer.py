"""
Atmospheric Complexity Framework (ACF)

Base Layer
==========

Base class for every map layer.
"""

from abc import ABC, abstractmethod


class BaseLayer(ABC):
    """
    Base class of every scientific layer.
    """

    def __init__(self, name="Layer"):

        self.id = id(self)

        self.name = name

        self.visible = True

        self.opacity = 1.0

        self.enabled = True

        self.zorder = 0

    ##################################################

    def show(self):

        self.visible = True

    ##################################################

    def hide(self):

        self.visible = False

    ##################################################

    def toggle(self):

        self.visible = not self.visible

    ##################################################

    def set_opacity(self, value):

        value = max(0.0, min(1.0, float(value)))

        self.opacity = value

    ##################################################

    def set_zorder(self, value):

        self.zorder = int(value)

    ##################################################

    @abstractmethod
    def render(self, axes):
        """
        Render the layer.
        """

    ##################################################

    def status(self):

        return {
            "id": self.id,
            "name": self.name,
            "visible": self.visible,
            "enabled": self.enabled,
            "opacity": self.opacity,
            "zorder": self.zorder,
        }
