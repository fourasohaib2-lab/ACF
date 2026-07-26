"""
Atmospheric Complexity Framework (ACF)

Wheel Controller
================

Mouse wheel zoom controller.
"""

from PySide6.QtCore import QObject, Signal


class WheelController(QObject):
    """
    Handles mouse wheel zoom.
    """

    ##################################################

    zoomInRequested = Signal()

    zoomOutRequested = Signal()

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.zoom_factor = 1.2

    ##################################################

    def wheel(self, event):
        """
        Handle wheel event.
        """

        delta = event.angleDelta().y()

        if delta > 0:

            self.zoomInRequested.emit()

        elif delta < 0:

            self.zoomOutRequested.emit()

    ##################################################

    def set_zoom_factor(
        self,
        factor,
    ):

        self.zoom_factor = float(factor)

    ##################################################

    def status(self):

        return {

            "zoom_factor": self.zoom_factor,

        }
