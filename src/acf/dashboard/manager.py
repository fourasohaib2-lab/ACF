"""
ACF Dashboard Manager
"""

from acf.dashboard.dashboard import Dashboard


class DashboardManager:
    """
    Gestionnaire principal des dashboards ACF.
    """

    ##################################################

    def __init__(self, window=None):

        self.window = window

        self.dashboard = None

        self._dashboards = {}

        if window is not None:

            self.dashboard = Dashboard(window)

    ##################################################

    def register(self, name, dashboard):
        """
        Register a dashboard.
        """

        self._dashboards[name] = dashboard

    ##################################################

    def unregister(self, name):
        """
        Remove a dashboard.
        """

        self._dashboards.pop(name, None)

    ##################################################

    def get(self, name):
        """
        Return dashboard.
        """

        return self._dashboards.get(name)

    ##################################################

    def load(self, name):
        """
        Load dashboard.
        """

        return self.get(name)

    ##################################################

    def available(self):
        """
        Return registered dashboard names.
        """

        return list(self._dashboards.keys())

    ##################################################

    def dashboards(self):
        """
        Return dashboard dictionary.
        """

        return self._dashboards

    ##################################################

    def initialize(self):

        if self.dashboard is not None:

            self.dashboard.initialize()

    ##################################################

    def get_panel(self, name):

        if self.dashboard is not None:

            return self.dashboard.get_panel(name)

        return None

    ##################################################

    def clear_project(self):

        if self.dashboard is not None:

            self.dashboard.clear_project()

    ##################################################

    def refresh(self):

        if self.dashboard is not None:

            self.dashboard.refresh()

    ##################################################

    def shutdown(self):

        if self.dashboard is not None:

            self.dashboard.shutdown()

    ##################################################

    def status(self):

        return {

            "window": self.window is not None,

            "dashboard": self.dashboard is not None,

            "registered_dashboards": len(self._dashboards),

        }
