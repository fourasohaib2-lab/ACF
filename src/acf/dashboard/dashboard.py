"""
ACF Dashboard
"""

from acf.dashboard.layout import DashboardLayout


class Dashboard:
    """
    Dashboard principal ACF.
    """

    ##################################################

    def __init__(self, window=None):

        #
        # Deux modes de fonctionnement :
        #
        # Dashboard("Weather")  -> utilisé par les tests
        #
        # Dashboard(main_window) -> utilisé par l'application
        #

        self.layout = None
        self.panels = {}

        if isinstance(window, str):
            self.name = window
            self.window = None

        else:
            self.window = window
            self.name = "Dashboard"

            if self.window is not None:
                self.layout = DashboardLayout(self.window)

    ##################################################

    def initialize(self):

        if self.layout is not None:
            self.panels = self.layout.build()

    ##################################################

    def get_panel(self, name):

        return self.panels.get(name)

    ##################################################

    def clear_project(self):
        """
        Nettoyage après fermeture d'un projet.
        """

        explorer = self.panels.get("explorer")

        if explorer and hasattr(explorer, "clear"):
            explorer.clear()

        map_view = self.panels.get("map")

        if map_view:
            if hasattr(map_view, "clear"):
                map_view.clear()

            if hasattr(map_view, "setText"):
                map_view.setText("Map View (No Project)")

        properties = self.panels.get("properties")

        if properties:
            widget = properties.widget()

            if widget and hasattr(widget, "clear"):
                widget.clear()

    ##################################################

    def refresh(self):

        pass

    ##################################################

    def shutdown(self):

        pass

    ##################################################

    def to_dict(self):
        """
        Convert dashboard to dictionary.
        """

        return {
            "name": self.name,
        }

    ##################################################

    @classmethod
    def from_dict(cls, data):
        """
        Create dashboard from dictionary.
        """

        return cls(data.get("name", "Dashboard"))
