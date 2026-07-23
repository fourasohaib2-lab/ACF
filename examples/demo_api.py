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
