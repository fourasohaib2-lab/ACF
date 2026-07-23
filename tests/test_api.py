import numpy as np

from acf.api.api import ACFAPI


def test_registry():

    api = ACFAPI()

    assert api.parameter("t2m") is not None


def test_analysis():

    api = ACFAPI()

    dataset = {
        "temperature": np.array([10,20,30])
    }

    report = api.analyze(dataset)

    assert "temperature" in report


def test_alerts():

    api = ACFAPI()

    api.register_alert_rule(
        "temperature",
        40,
        "warning",
        "Extreme Heat"
    )

    dataset = {
        "temperature": np.array([42])
    }

    alerts = api.alerts(dataset)

    assert len(alerts) == 1
