"""
Atmospheric Complexity Framework (ACF)

Professional Map Camera

Controls map navigation for the ACF Map Engine.
"""

from PySide6.QtCore import QObject, Signal


class MapCamera(QObject):
    """
    Professional scientific map camera.

    Responsibilities
    ----------------
    - Camera center
    - Zoom
    - Extent
    - Projection
    - Navigation state
    """

    ##################################################
    # Signals
    ##################################################

    cameraChanged = Signal()

    zoomChanged = Signal(float)

    centerChanged = Signal(float, float)

    projectionChanged = Signal(str)

    extentChanged = Signal(object)

##################################################

def __init__(self, parent=None):

    super().__init__(parent)

    self.initialize()
##################################################

def initialize(self):
    """
    Initialize camera state.
    """

    self.center_longitude = 0.0

    self.center_latitude = 0.0

    self.zoom_level = 1.0

    self.min_zoom = 0.25

    self.max_zoom = 30.0

    self.rotation = 0.0

    self.projection_name = "PlateCarree"

    self.extent = [
        -180.0,
        180.0,
        -90.0,
        90.0,
    ]

    self.initialized = True
##################################################

def set_center(
    self,
    longitude,
    latitude,
):
    """
    Set camera center.
    """

    self.center_longitude = float(longitude)

    self.center_latitude = float(latitude)

    self.centerChanged.emit(
        self.center_longitude,
        self.center_latitude,
    )

    self.cameraChanged.emit()


##################################################

def center(self):

    return (
        self.center_longitude,
        self.center_latitude,
    )


##################################################

def move(
    self,
    delta_longitude,
    delta_latitude,
):
    """
    Relative movement.
    """

    self.set_center(
        self.center_longitude + delta_longitude,
        self.center_latitude + delta_latitude,
    )


##################################################

def pan(
    self,
    delta_longitude,
    delta_latitude,
):
    """
    Alias for move().
    """

    self.move(
        delta_longitude,
        delta_latitude,
    )

##################################################

def zoom(self):

    return self.zoom_level


##################################################

def set_zoom(
    self,
    value,
):
    """
    Set zoom level.
    """

    value = max(
        self.min_zoom,
        min(
            self.max_zoom,
            float(value),
        ),
    )

    if value == self.zoom_level:
        return

    self.zoom_level = value

    self.zoomChanged.emit(
        self.zoom_level
    )

    self.cameraChanged.emit()


##################################################

def zoom_in(
    self,
    factor=1.2,
):

    self.set_zoom(
        self.zoom_level * factor
    )


##################################################

def zoom_out(
    self,
    factor=1.2,
):

    self.set_zoom(
        self.zoom_level / factor
    )
##################################################

def set_projection(
    self,
    projection,
):
    """
    Set map projection.
    """

    self.projection_name = projection

    self.projectionChanged.emit(
        projection
    )

    self.cameraChanged.emit()


##################################################

def projection(self):

    return self.projection_name
##################################################

def set_extent(
    self,
    west,
    east,
    south,
    north,
):
    """
    Set visible extent.
    """

    self.extent = [
        west,
        east,
        south,
        north,
    ]

    self.extentChanged.emit(
        self.extent
    )

    self.cameraChanged.emit()


##################################################

def fit_world(self):

    self.set_extent(
        -180,
        180,
        -90,
        90,
    )


##################################################

def fit_extent(
    self,
    extent,
):

    self.set_extent(
        extent[0],
        extent[1],
        extent[2],
        extent[3],
    )
##################################################

def reset(self):

    self.initialize()

    self.cameraChanged.emit()


##################################################

def status(self):

    return {

        "initialized": self.initialized,

        "center": self.center(),

        "zoom": self.zoom_level,

        "projection": self.projection_name,

        "extent": self.extent,

        "rotation": self.rotation,

    }

