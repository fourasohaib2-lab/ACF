"""
Atmospheric Complexity Framework (ACF)

Projection Manager
==================

Central management of map projections.
"""

from PySide6.QtCore import QObject, Signal

try:
    import cartopy.crs as ccrs
    HAS_CARTOPY = True
except Exception:
    HAS_CARTOPY = False


class ProjectionManager(QObject):
    """
    Professional projection manager.
    """

    projectionChanged = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.initialize()
    ##################################################

    def initialize(self):
        """
        Initialize the projection manager.
        """

        self.current_name = "PlateCarree"

        self.current_projection = None

        self._projections = {}

        if HAS_CARTOPY:

            self._projections = {

                "PlateCarree": ccrs.PlateCarree(),

                "Mercator": ccrs.Mercator(),

                "LambertConformal": ccrs.LambertConformal(),

                "NorthPolarStereo": ccrs.NorthPolarStereo(),

                "SouthPolarStereo": ccrs.SouthPolarStereo(),

                "Robinson": ccrs.Robinson(),

                "Orthographic": ccrs.Orthographic(),

            }

            self.current_projection = (
                self._projections[self.current_name]
            )

    ##################################################

    def available_projections(self):
        """
        Return all available projections.
        """

        return sorted(
            self._projections.keys()
        )

    ##################################################

    def current(self):
        """
        Return current Cartopy projection.
        """

        return self.current_projection

    ##################################################

    def current_projection_name(self):
        """
        Return current projection name.
        """

        return self.current_name
    ##################################################

    def set_projection(
        self,
        name,
    ):
        """
        Change current projection.
        """

        if name not in self._projections:
            return False

        self.current_name = name

        self.current_projection = (
            self._projections[name]
        )

        self.projectionChanged.emit(
            name
        )

        return True
    ##################################################
    ##################################################

    def status(self):
        """
        Diagnostic information.
        """

        return {

            "cartopy": HAS_CARTOPY,

            "projection": self.current_name,

            "available": self.available_projections(),

        }
    def status(self):
        """
        Diagnostic information.
        """

        return {

            "cartopy": HAS_CARTOPY,

            "projection": self.current_name,

            "available": self.available_projections(),

        }
