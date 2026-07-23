"""
ACF Dashboard
"""

from acf.dashboard.layout import DashboardLayout


class Dashboard:
    """
    Dashboard principal ACF.

    Peut être utilisé :
      - en mode test : Dashboard("Weather")
      - en mode GUI  : Dashboard(window)
    """

    def __init__(self, arg=None):

        self.layout = None
        self.panels = {}

        # Mode GUI
        if hasattr(arg, "setCentralWidget"):
            self.window = arg
            self.name = "Main Dashboard"
            self.layout = DashboardLayout(arg)

        # Mode Test
        else:
            self.window = None
            self.name = arg if isinstance(arg, str) else "Dashboard"

    def initialize(self):
        if self.layout is not None:
            self.panels = self.layout.build()

    def refresh(self):
        pass

    def shutdown(self):
        pass
