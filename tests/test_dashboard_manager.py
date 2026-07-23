from acf.dashboard.dashboard import Dashboard
from acf.dashboard.manager import DashboardManager


def test_dashboard_registration():

    manager = DashboardManager()

    dashboard = Dashboard("Main")

    manager.register("main", dashboard)

    assert "main" in manager.available()


def test_dashboard_loading():

    manager = DashboardManager()

    dashboard = Dashboard("Weather")

    manager.register("weather", dashboard)

    loaded = manager.load("weather")

    assert loaded.name == "Weather"

