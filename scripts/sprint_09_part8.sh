#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " ACF Sprint 09 - Partie 8"
echo " Core API"
echo "========================================"

mkdir -p "$PROJECT/src/acf/api"

touch "$PROJECT/src/acf/api/__init__.py"

##################################################
# API
##################################################

cat > "$PROJECT/src/acf/api/api.py" << 'EOF'
"""
Atmospheric Complexity Framework API
"""

from acf.core.default_parameters import create_registry
from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer
from acf.ai.forecast.forecast_assistant import ForecastAssistant
from acf.ai.alerts.weather_alert_engine import WeatherAlertEngine


class ACFAPI:

    def __init__(self):

        self.registry = create_registry()

        self.analyzer = DatasetAnalyzer()

        self.forecast = ForecastAssistant()

        self.alert_engine = WeatherAlertEngine()

    ##################################################

    def parameters(self):

        return self.registry.all()

    ##################################################

    def parameter(self, parameter_id):

        return self.registry.get(parameter_id)

    ##################################################

    def analyze(self, dataset):

        return self.analyzer.analyze(dataset)

    ##################################################

    def forecast_report(self, dataset):

        return self.forecast.generate_report(dataset)

    ##################################################

    def register_alert_rule(
        self,
        variable,
        threshold,
        level,
        message
    ):

        self.alert_engine.register_rule(
            variable,
            threshold,
            level,
            message
        )

    ##################################################

    def alerts(self, dataset):

        return self.alert_engine.analyze(dataset)
EOF

##################################################
# TESTS
##################################################

cat > "$PROJECT/tests/test_api.py" << 'EOF'
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
EOF

##################################################
# EXEMPLE
##################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_api.py" << 'EOF'
import numpy as np

from acf.api.api import ACFAPI

api = ACFAPI()

print("=== Registered Parameters ===")

for parameter in api.parameters():

    print(parameter.id, "-", parameter.name)

dataset = {

    "temperature": np.random.uniform(20,45,(50,50)),

    "humidity": np.random.uniform(30,90,(50,50))

}

print()

print("=== Analysis ===")

print(api.analyze(dataset))

print()

print("=== Forecast ===")

print(api.forecast_report(dataset))

api.register_alert_rule(

    "temperature",

    40,

    "warning",

    "Extreme Heat"

)

print()

print("=== Alerts ===")

print(api.alerts(dataset))
EOF

echo
echo "ACF API installed successfully."
