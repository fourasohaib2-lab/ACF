"""
AI Dashboard Widget

NOTE (Physics Guard, 2026-09-06 Tier C sweep): not constructed
anywhere in src/ (verified by grep - only tests/test_ai_dashboard.py
uses it). Real, correct, honest code in itself - set_parameters()/
set_alerts()/set_forecast() just display whatever text they're
handed, no computation or claim of their own - just currently
unwired. Console/Explorer, its siblings in this package, ARE real
(acf.dashboard.layout.DashboardLayout.build(), reached from a real
button in acf.gui.esoc.esoc_window.ESOCWindow._open_classic_dashboard).
"""

from PySide6.QtWidgets import (
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
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

        self.parameters.setPlainText("\n".join(parameters))

    ##################################################

    def set_alerts(self, alerts):

        lines = []

        for alert in alerts:
            lines.append(f"[{alert['level'].upper()}] {alert['message']}")

        self.alerts.setPlainText("\n".join(lines))

    ##################################################

    def set_forecast(self, report):

        self.forecast.setPlainText("\n".join(report))
