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
