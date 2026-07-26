"""
Atmospheric Complexity Framework (ACF)

Map Camera
==========

Controls map navigation.
"""


from PySide6.QtCore import QObject, Signal


class MapCamera(QObject):
    """
    Scientific map navigation controller.
    """


    cameraChanged = Signal()


    ##################################################

    def __init__(self, parent=None):

        super().__init__(parent)

        self.center_longitude = 0.0

        self.center_latitude = 0.0

        self.zoom_level = 1.0

        self.min_zoom = 0.1

        self.max_zoom = 20.0

        self.extent = None


    ##################################################

    def set_center(
        self,
        longitude,
        latitude,
    ):

        self.center_longitude = longitude

        self.center_latitude = latitude

        self.cameraChanged.emit()


    ##################################################

    def center(self):

        return (

            self.center_longitude,

            self.center_latitude,

        )


    ##################################################

    def zoom_in(
        self,
        factor=1.2,
    ):

        self.zoom_level *= factor

        self.zoom_level = min(
            self.zoom_level,
            self.max_zoom,
        )

        self.cameraChanged.emit()


    ##################################################

    def zoom_out(
        self,
        factor=1.2,
    ):

        self.zoom_level /= factor

        self.zoom_level = max(
            self.zoom_level,
            self.min_zoom,
        )

        self.cameraChanged.emit()


    ##################################################

    def reset(self):

        self.center_longitude = 0.0

        self.center_latitude = 0.0

        self.zoom_level = 1.0

        self.extent = None

        self.cameraChanged.emit()


    ##################################################

    def set_extent(
        self,
        extent,
    ):

        self.extent = extent

        self.cameraChanged.emit()


    ##################################################

    def status(self):

        return {

            "center":

                self.center(),

            "zoom":

                self.zoom_level,

            "extent":

                self.extent,

        }

