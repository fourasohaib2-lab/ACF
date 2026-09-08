"""
Atmospheric Complexity Framework (ACF)

Professional Status Bar

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): never
constructed anywhere (confirmed by grep across src/). This class itself
is genuinely correct and functional (real message/coordinates/zoom/
projection QLabels on a real status bar) - unlike this package's own
menu_bar.py/tool_bar.py, this isn't a dead-on-arrival skeleton. It is
superseded in practice: ESOCWindow already has its own, more complete
ESOCStatusBar (HPC connection, sim time, forecast hour, hardware,
streams, dataset, layer, projection, workspace mode - see
esoc_statusbar.py, this session's own earlier fixes to it), and
ClassicDashboardWindow's MenuManager already uses Qt's own default
QMainWindow status bar via window.statusBar().showMessage(...) - no
window in this application currently needs this specific, simpler
status bar. Not deleted per project convention.
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

        self.coordinates.setText(f"Lon: {longitude:.2f}   Lat: {latitude:.2f}")

    ##################################################

    def set_zoom(self, zoom):

        self.zoom.setText(f"Zoom: {zoom:.1f}x")

    ##################################################

    def set_projection(self, projection):

        self.projection.setText(f"Projection: {projection}")
