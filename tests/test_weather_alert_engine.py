import numpy as np

from acf.ai.alerts.weather_alert_engine import WeatherAlertEngine


def test_alert():

    engine = WeatherAlertEngine()

    engine.register_rule(
        "temperature",
        40,
        "warning",
        "Extreme heat"
    )

    dataset = {
        "temperature": np.array([38,41,43])
    }

    alerts = engine.analyze(dataset)

    assert len(alerts) == 1

    assert alerts[0]["level"] == "warning"


def test_no_alert():

    engine = WeatherAlertEngine()

    engine.register_rule(
        "wind_speed",
        100,
        "danger",
        "Violent wind"
    )

    dataset = {
        "wind_speed": np.array([20,25,30])
    }

    alerts = engine.analyze(dataset)

    assert alerts == []
