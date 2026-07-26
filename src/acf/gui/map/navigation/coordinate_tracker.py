"""
Atmospheric Complexity Framework (ACF)

Coordinate Tracker
==================

Tracks mouse geographic coordinates.
"""

from PySide6.QtCore import QObject, Signal


class CoordinateTracker(QObject):
    """
    Mouse coordinate tracker.
    """

    ##################################################

    coordinatesChanged = Signal(float, float)

    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.longitude = 0.0
        self.latitude = 0.0

    ##################################################

    def set_coordinates(
        self,
        longitude,
        latitude,
    ):

        self.longitude = float(longitude)
        self.latitude = float(latitude)

        self.coordinatesChanged.emit(
            self.longitude,
            self.latitude,
        )

    ##################################################

    def coordinates(self):

        return (
            self.longitude,
            self.latitude,
        )

    ##################################################

    def reset(self):

        self.set_coordinates(
            0.0,
            0.0,
        )

    ##################################################

    def status(self):

        return {

            "longitude": self.longitude,

            "latitude": self.latitude,

        }
