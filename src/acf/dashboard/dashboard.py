"""
ACF Dashboard
"""

from acf.dashboard.layout import DashboardLayout


class Dashboard:
    """
    Dashboard principal ACF.
    """

    def __init__(self, window=None):

        self.window = window

        self.layout = None

        self.panels = {}

        if window:

            self.layout = DashboardLayout(window)


    ##################################################

    def initialize(self):

        if self.layout:

            self.panels = self.layout.build()


    ##################################################

    def get_panel(self, name):

        return self.panels.get(name)


    ##################################################

    def clear_project(self):

        """
        Nettoyage de l'interface
        après fermeture d'un projet.
        """

        # Explorer

        explorer = self.panels.get(
            "explorer"
        )

        if explorer:

            explorer.clear()


        # Carte

        map_view = self.panels.get(
            "map"
        )

        if map_view:

            map_view.clear()

            map_view.setText(
                "Map View (No Project)"
            )


        # Propriétés

        properties = self.panels.get(
            "properties"
        )

        if properties:

            widget = properties.widget()

            if widget and hasattr(
                widget,
                "clear"
            ):

                widget.clear()



    ##################################################

    def refresh(self):

        pass


    ##################################################

    def shutdown(self):

        pass
