#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================"
echo " ACF Sprint 09 - Partie 7"
echo " AI Dashboard"
echo "======================================"

mkdir -p "$PROJECT/src/acf/gui/widgets"

####################################################
# AI DASHBOARD
####################################################

cat > "$PROJECT/src/acf/gui/widgets/ai_dashboard.py" << 'EOF'
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
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_ai_dashboard.py" << 'EOF'
from acf.gui.widgets.ai_dashboard import AIDashboard


def test_dashboard_creation(qtbot):

    widget = AIDashboard()

    qtbot.addWidget(widget)

    assert widget is not None


def test_parameters(qtbot):

    widget = AIDashboard()

    qtbot.addWidget(widget)

    widget.set_parameters(
        [
            "Temperature",
            "Humidity",
            "Wind"
        ]
    )

    assert "Temperature" in widget.parameters.toPlainText()
EOF

####################################################
# DEMO
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_ai_dashboard.py" << 'EOF'
from PySide6.QtWidgets import QApplication

from acf.gui.widgets.ai_dashboard import AIDashboard

app = QApplication([])

dashboard = AIDashboard()

dashboard.set_parameters([
    "Temperature",
    "Pressure",
    "Humidity",
    "Wind Speed",
    "CAPE"
])

dashboard.set_alerts([
    {
        "level":"warning",
        "message":"Extreme Heat"
    },
    {
        "level":"danger",
        "message":"Severe Thunderstorm"
    }
])

dashboard.set_forecast([
    "Warm weather expected.",
    "Thunderstorm risk during the afternoon.",
    "Strong wind possible."
])

dashboard.resize(500,700)
dashboard.show()

app.exec()
EOF

echo
echo "AI Dashboard installed successfully."
