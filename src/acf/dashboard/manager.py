"""
ACF Dashboard Manager
"""

from acf.dashboard.dashboard import Dashboard


class DashboardManager:
    """
    Gestionnaire du dashboard ACF.
    """


    def __init__(self, window=None):

        self.window = window

        self.dashboard = None


        if window:

            self.dashboard = Dashboard(
                window
            )


    ##################################################

    def initialize(self):

        if self.dashboard:

            self.dashboard.initialize()



    ##################################################

    def get_panel(self, name):

        if self.dashboard:

            return self.dashboard.get_panel(
                name
            )

        return None



    ##################################################

    def clear_project(self):

        if self.dashboard:

            self.dashboard.clear_project()



    ##################################################

    def refresh(self):

        if self.dashboard:

            self.dashboard.refresh()



    ##################################################

    def shutdown(self):

        if self.dashboard:

            self.dashboard.shutdown()
