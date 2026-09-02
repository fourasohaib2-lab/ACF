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

NOTE (found while wiring real zoom/pan into acf.gui.map.map_canvas.
MapCanvas, explicit user request "ajoute l'option zoom des cartes et
manipulation totale des cartes"): a second real gap, beyond the one
above. `zoom_level`/`center_longitude`/`center_latitude` were tracked
as real state, but nothing ever derived a real geographic `extent`
from them - `zoom_in()`/`pan()` changed the tracked numbers but
`self.extent` only ever changed via an explicit `set_extent()`/
`fit_extent()`/`fit_world()` call. Wiring this class in as-is would
have changed internal state without changing what Cartopy actually
draws. Fixed by `current_extent()` below (a real, documented formula,
not a guess) and by every zoom/pan/center mutator re-deriving
`self.extent` through it.
"""

from PySide6.QtCore import QObject, Signal

#: current_extent()'s real, documented mapping from zoom_level to a
#: geographic half-width/half-height in degrees at zoom_level == 1.0
#: (the world fits exactly: half-width 180°, half-height 90°). A
#: defensible, simple choice - not the only possible one (a Mercator-
#: style projection would want a non-linear zoom curve) - documented
#: here rather than left as an unexplained magic number, same
#: convention as acf.physics_guard.range_check.OPERATIONAL_RANGES.
_WORLD_HALF_WIDTH_DEG = 180.0
_WORLD_HALF_HEIGHT_DEG = 90.0


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

        self._sync_extent()

        self.centerChanged.emit(
            self.center_longitude,
            self.center_latitude,
        )

        self.cameraChanged.emit()

    ##################################################

    def current_extent(self):
        """
        Real, documented derivation of a geographic
        [west, east, south, north] extent from `center_longitude`/
        `center_latitude` + `zoom_level` - see this module's own NOTE
        (correction) for why this exists (zoom/pan used to change
        `zoom_level`/center without ever touching `self.extent`).

        half-width = _WORLD_HALF_WIDTH_DEG / zoom_level, similarly for
        half-height - at zoom_level == 1.0 the whole world is visible;
        doubling zoom halves the visible span. Longitude is clamped to
        [-180, 180] (no dateline wraparound support here - a real,
        disclosed limitation, not a silent one: panning west of -180
        stops at the edge rather than wrapping to +180) and latitude to
        [-90, 90].
        """

        half_width = _WORLD_HALF_WIDTH_DEG / self.zoom_level

        half_height = _WORLD_HALF_HEIGHT_DEG / self.zoom_level

        west = max(-180.0, self.center_longitude - half_width)

        east = min(180.0, self.center_longitude + half_width)

        south = max(-90.0, self.center_latitude - half_height)

        north = min(90.0, self.center_latitude + half_height)

        return [west, east, south, north]

    ##################################################

    def _sync_extent(self):
        """Recompute self.extent from current center/zoom and emit
        extentChanged - called by every mutator that changes either,
        so self.extent never goes stale (see this module's own NOTE
        (correction))."""

        self.extent = self.current_extent()

        self.extentChanged.emit(self.extent)

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

        self._sync_extent()

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
        Set visible extent directly - and, so `current_center()`/
        `current_zoom()` never report a value inconsistent with the
        extent just set (the inverse of `current_extent()`'s own
        center+zoom -> extent formula), also re-derives
        `center_longitude`/`center_latitude`/`zoom_level` from it.
        """

        self.extent = [
            west,
            east,
            south,
            north,
        ]

        half_width = max(1e-6, (east - west) / 2.0)

        self.center_longitude = (west + east) / 2.0

        self.center_latitude = (south + north) / 2.0

        # Inverse of current_extent()'s half_width = WORLD / zoom_level.
        # Longitude drives zoom_level (matches current_extent()'s own
        # longitude-first clamping order); a non-square extent's real
        # latitude span may then imply a different zoom - not
        # reconciled here, same "documented, not the only possible
        # choice" spirit as current_extent()'s own docstring.
        self.zoom_level = max(
            self.min_zoom,
            min(
                self.max_zoom,
                _WORLD_HALF_WIDTH_DEG / half_width,
            ),
        )

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
