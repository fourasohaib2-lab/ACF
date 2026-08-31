"""
Atmospheric Complexity Framework (ACF)

Map Navigation
==============

Navigation mixin used by MapCanvas.

Handles:

- Zoom
- Pan
- Center
- Extent
- World view
"""


class NavigationMixin:
    ##################################################
    # Zoom
    ##################################################

    def zoom_in(self, factor=1.2):

        self.camera.zoom_in(factor)

        self.refresh()

    ##################################################

    def zoom_out(self, factor=1.2):

        self.camera.zoom_out(factor)

        self.refresh()

    ##################################################

    def set_zoom(self, zoom):

        zoom = max(
            self.camera.min_zoom,
            min(
                self.camera.max_zoom,
                zoom,
            ),
        )

        self.camera.zoom_level = zoom

        self.refresh()

    ##################################################

    def current_zoom(self):

        return self.camera.zoom_level

    ##################################################
    # Center
    ##################################################

    def set_center(
        self,
        longitude,
        latitude,
    ):

        self.camera.set_center(
            longitude,
            latitude,
        )

        self.refresh()

    ##################################################

    def current_center(self):

        return self.camera.center()

    ##################################################
    # Pan
    ##################################################

    def pan(
        self,
        dx,
        dy,
    ):

        lon, lat = self.camera.center()

        self.camera.set_center(
            lon + dx,
            lat + dy,
        )

        self.refresh()

    ##################################################

    def pan_left(self, step=5):

        self.pan(
            -step,
            0,
        )

    ##################################################

    def pan_right(self, step=5):

        self.pan(
            step,
            0,
        )

    ##################################################

    def pan_up(self, step=5):

        self.pan(
            0,
            step,
        )

    ##################################################

    def pan_down(self, step=5):

        self.pan(
            0,
            -step,
        )

    ##################################################
    # Extent
    ##################################################

    def fit_extent(self, extent):
        """
        extent

        (
            west,
            east,
            south,
            north,
        )
        """

        self.camera.set_extent(
            extent,
        )

        self.refresh()

    ##################################################

    def current_extent(self):

        return self.camera.extent

    ##################################################
    # World
    ##################################################

    def fit_world(self):

        self.fit_extent(
            (
                -180,
                180,
                -90,
                90,
            )
        )

    ##################################################
    # Reset
    ##################################################

    def reset_view(self):

        self.camera.reset()

        self.refresh()
