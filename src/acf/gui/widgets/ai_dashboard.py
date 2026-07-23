"""
AI Dashboard Widget
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
)


class AIDashboard(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Artificial Intelligence")

        title.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        self.parameters = QTextEdit()
        self.parameters.setReadOnly(True)

        self.alerts = QTextEdit()
        self.alerts.setReadOnly(True)

        self.forecast = QTextEdit()
        self.forecast.setReadOnly(True)

        layout.addWidget(QLabel("Detected Parameters"))
        layout.addWidget(self.parameters)

        layout.addWidget(QLabel("Weather Alerts"))
        layout.addWidget(self.alerts)

        layout.addWidget(QLabel("Forecast Assistant"))
        layout.addWidget(self.forecast)

    ##################################################

    def set_parameters(self, parameters):

        self.parameters.setPlainText(
            "\n".join(parameters)
        )

    ##################################################

    def set_alerts(self, alerts):

        lines = []

        for alert in alerts:

            lines.append(
                f"[{alert['level'].upper()}] "
                f"{alert['message']}"
            )

        self.alerts.setPlainText("\n".join(lines))

    ##################################################

    def set_forecast(self, report):

        self.forecast.setPlainText(
            "\n".join(report)
        )
