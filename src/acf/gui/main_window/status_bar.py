"""
Atmospheric Complexity Framework (ACF)

Professional Status Bar
"""

from PySide6.QtWidgets import QLabel


class ACFStatusBar:
    """
    Professional application status bar.
    """

    def __init__(self, window):

        self.window = window

        self.status_bar = window.statusBar()

        self.message = QLabel("Ready")

        self.coordinates = QLabel("Lon: --  Lat: --")

        self.zoom = QLabel("Zoom: 100%")

        self.projection = QLabel("Projection: PlateCarree")

        self.status_bar.addWidget(self.message)

        self.status_bar.addPermanentWidget(self.coordinates)

        self.status_bar.addPermanentWidget(self.zoom)

        self.status_bar.addPermanentWidget(self.projection)

    ##################################################

    def set_message(self, text):

        self.message.setText(text)

    ##################################################

    def set_coordinates(
        self,
        longitude,
        latitude,
    ):

        self.coordinates.setText(
            f"Lon: {longitude:.2f}   Lat: {latitude:.2f}"
        )

    ##################################################

    def set_zoom(self, zoom):

        self.zoom.setText(
            f"Zoom: {zoom:.1f}x"
        )

    ##################################################

    def set_projection(self, projection):

        self.projection.setText(
            f"Projection: {projection}"
        )

