#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " ACF Sprint 09 - Partie 4"
echo " Forecast Assistant"
echo "========================================"

mkdir -p "$PROJECT/src/acf/ai/forecast"

touch "$PROJECT/src/acf/ai/forecast/__init__.py"

####################################################
# FORECAST ASSISTANT
####################################################

cat > "$PROJECT/src/acf/ai/forecast/forecast_assistant.py" << 'EOF'
"""
Forecast Assistant
"""

from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer


class ForecastAssistant:
    """
    Génère un premier résumé météorologique.
    """

    def __init__(self):

        self.analyzer = DatasetAnalyzer()

    ##################################################

    def generate_report(self, dataset):

        analysis = self.analyzer.analyze(dataset)

        report = []

        ##################################################
        # TEMPERATURE
        ##################################################

        if "temperature" in analysis:

            mean = analysis["temperature"]["mean"]

            if mean < 0:
                report.append("Cold conditions expected.")

            elif mean < 15:
                report.append("Cool weather expected.")

            elif mean < 30:
                report.append("Warm weather expected.")

            else:
                report.append("Very hot conditions expected.")

        ##################################################
        # PRESSURE
        ##################################################

        if "pressure" in analysis:

            pressure = analysis["pressure"]["mean"]

            if pressure < 1000:
                report.append("Possible low-pressure system.")

            elif pressure > 1025:
                report.append("Stable high-pressure conditions.")

        ##################################################
        # HUMIDITY
        ##################################################

        if "humidity" in analysis:

            humidity = analysis["humidity"]["mean"]

            if humidity > 80:
                report.append("High humidity.")

        return report
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_forecast_assistant.py" << 'EOF'
import numpy as np

from acf.ai.forecast.forecast_assistant import ForecastAssistant


def test_report():

    assistant = ForecastAssistant()

    dataset = {

        "temperature": np.array([30,31,32]),

        "pressure": np.array([995,997,998]),

        "humidity": np.array([85,88,90])

    }

    report = assistant.generate_report(dataset)

    assert len(report) >= 3

    assert any("hot" in line.lower() for line in report)

    assert any("pressure" in line.lower() for line in report)
EOF

####################################################
# EXAMPLE
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_forecast_assistant.py" << 'EOF'
import numpy as np

from acf.ai.forecast.forecast_assistant import ForecastAssistant

assistant = ForecastAssistant()

dataset = {

    "temperature": np.random.uniform(28,35,(100,100)),

    "pressure": np.random.uniform(990,1000,(100,100)),

    "humidity": np.random.uniform(80,95,(100,100))

}

report = assistant.generate_report(dataset)

print()

print("Forecast Report")

print("----------------")

for line in report:

    print("-", line)
EOF

echo
echo "Forecast Assistant installed successfully."

