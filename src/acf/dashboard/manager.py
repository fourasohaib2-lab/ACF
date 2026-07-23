"""
ACF Dashboard Manager
"""

from acf.dashboard.dashboard import Dashboard


class DashboardManager:
    """
    Gestionnaire des dashboards ACF.
    """

    def __init__(self, window=None):

        self.window = window
        self.dashboard = None

        self._dashboards = {}
        self.current_dashboard = None

        if window is not None:
            self.dashboard = Dashboard(window)

    ##################################################

    def initialize(self):

        if self.dashboard is not None:
            self.dashboard.initialize()

    ##################################################

    def refresh(self):

        if self.dashboard is not None:
            self.dashboard.refresh()

    ##################################################

    def shutdown(self):

        if self.dashboard is not None:
            self.dashboard.shutdown()

    ##################################################
    # API de gestion des dashboards
    ##################################################

    def register(self, name, dashboard):

        self._dashboards[name] = dashboard

    def unregister(self, name):

        self._dashboards.pop(name, None)

    def load(self, name):

        if name not in self._dashboards:
            raise ValueError(f"Dashboard '{name}' not found.")

        self.current_dashboard = self._dashboards[name]
        return self.current_dashboard

    def current(self):

        return self.current_dashboard

    def available(self):

        return sorted(self._dashboards.keys())
