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
