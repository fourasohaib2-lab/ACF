from PySide6.QtWidgets import QApplication

from acf.gui.widgets.ai_dashboard import AIDashboard

app = QApplication([])

dashboard = AIDashboard()

dashboard.set_parameters(["Temperature", "Pressure", "Humidity", "Wind Speed", "CAPE"])

dashboard.set_alerts(
    [{"level": "warning", "message": "Extreme Heat"}, {"level": "danger", "message": "Severe Thunderstorm"}]
)

dashboard.set_forecast(["Warm weather expected.", "Thunderstorm risk during the afternoon.", "Strong wind possible."])

dashboard.resize(500, 700)
dashboard.show()

app.exec()
