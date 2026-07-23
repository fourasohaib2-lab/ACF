#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " ACF Sprint 09 - Partie 5"
echo " Weather Alert Engine"
echo "========================================"

mkdir -p "$PROJECT/src/acf/ai/alerts"

touch "$PROJECT/src/acf/ai/alerts/__init__.py"

####################################################
# WEATHER ALERT ENGINE
####################################################

cat > "$PROJECT/src/acf/ai/alerts/weather_alert_engine.py" << 'EOF'
"""
Weather Alert Engine
"""

import numpy as np


class WeatherAlertEngine:

    def __init__(self):

        self.rules = []

    ##################################################

    def register_rule(self, variable, threshold, level, message):

        self.rules.append({
            "variable": variable,
            "threshold": threshold,
            "level": level,
            "message": message
        })

    ##################################################

    def analyze(self, dataset):

        alerts = []

        for rule in self.rules:

            variable = rule["variable"]

            if variable not in dataset:
                continue

            values = np.asarray(dataset[variable])

            maximum = float(np.nanmax(values))

            if maximum >= rule["threshold"]:

                alerts.append({
                    "variable": variable,
                    "level": rule["level"],
                    "value": maximum,
                    "message": rule["message"]
                })

        return alerts
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_weather_alert_engine.py" << 'EOF'
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
EOF

####################################################
# DEMO
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_weather_alert.py" << 'EOF'
import numpy as np

from acf.ai.alerts.weather_alert_engine import WeatherAlertEngine

engine = WeatherAlertEngine()

engine.register_rule(
    "temperature",
    40,
    "warning",
    "Extreme heat"
)

engine.register_rule(
    "wind_speed",
    90,
    "danger",
    "Violent wind"
)

dataset = {

    "temperature": np.random.uniform(20,45,(100,100)),

    "wind_speed": np.random.uniform(10,120,(100,100))

}

alerts = engine.analyze(dataset)

print()

print("Detected Alerts")

print("----------------")

for alert in alerts:

    print(alert)
EOF

echo
echo "Weather Alert Engine installed successfully."
