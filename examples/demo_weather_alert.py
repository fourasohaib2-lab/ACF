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
