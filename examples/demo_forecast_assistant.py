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
