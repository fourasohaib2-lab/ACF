"""
Atmospheric Complexity Framework (ACF)

Zoom Controller
===============

Professional zoom manager.
"""

from PySide6.QtCore import QObject, Signal


class ZoomController(QObject):
    """
    Controls map zoom level.
    """

    ##################################################

    zoomChanged = Signal(float)

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.initialize()

    ##################################################

    def initialize(self):

        self.zoom = 1.0

        self.minimum = 0.25

        self.maximum = 30.0

        self.factor = 1.20

    ##################################################

    def zoom_in(self):

        self.set_zoom(
            self.zoom * self.factor
        )

    ##################################################

    def zoom_out(self):

        self.set_zoom(
            self.zoom / self.factor
        )

    ##################################################

    def set_zoom(self, value):

        value = max(
            self.minimum,
            min(self.maximum, float(value))
        )

        if value == self.zoom:
            return

        self.zoom = value

        self.zoomChanged.emit(
            self.zoom
        )

    ##################################################

    def reset(self):

        self.set_zoom(1.0)

    ##################################################

    def status(self):

        return {

            "zoom": self.zoom,

            "minimum": self.minimum,

            "maximum": self.maximum,

            "factor": self.factor,

        }
