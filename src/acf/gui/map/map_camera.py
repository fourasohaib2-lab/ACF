"""
Atmospheric Complexity Framework (ACF)

Professional Map Camera

Controls map navigation for the ACF Map Engine.

NOTE (correction — severe): every method below (__init__, initialize,
set_center, center, move, pan, zoom, set_zoom, zoom_in, zoom_out,
set_projection, projection, set_extent, fit_world, fit_extent, reset,
status) was defined at MODULE level (a dedent left them outside the
class body entirely - only the 5 Signal declarations remained inside
MapCamera). MapCamera() constructed successfully (falling back to
QObject's own __init__, so no camera state was ever set - not even
center_longitude/center_latitude/zoom_level) but had none of its own
methods at all: MapCamera().set_center(1.0, 2.0) raised
"AttributeError: 'MapCamera' object has no attribute 'set_center'".
The entire map camera (pan/zoom/projection/extent) was non-functional.
Not currently called from anywhere else in the codebase and had no
test coverage to catch it - fixed anyway, matching this session's
"fix a broken component even if currently unused" precedent (see
acf.models.base_model.BaseWeatherModel's own NOTE (correction)).
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

        self.zoomChanged.emit(self.zoom_level)

        self.cameraChanged.emit()

    ##################################################

    def zoom_in(
        self,
        factor=1.2,
    ):

        self.set_zoom(self.zoom_level * factor)

    ##################################################

    def zoom_out(
        self,
        factor=1.2,
    ):

        self.set_zoom(self.zoom_level / factor)

    ##################################################

    def set_projection(
        self,
        projection,
    ):
        """
        Set map projection.
        """

        self.projection_name = projection

        self.projectionChanged.emit(projection)

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

        self.extentChanged.emit(self.extent)

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
