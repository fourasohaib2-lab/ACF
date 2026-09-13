from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_config_bar import ConfigBar


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_config_bar_shows_real_run_metadata(qapp, qtbot):
    bar = ConfigBar()
    qtbot.addWidget(bar)
    bar.update_from_config(
        {
            "model": "AROME",
            "cycle": "20250426 12 UTC",
            "forecast_hour": "+12h",
            "domain": "EUROPE",
            "resolution_km": 2.5,
            "grid": "Lambert",
            "vertical_levels": 90,
        }
    )
    assert "AROME" in bar.model_label.text()
    assert "EUROPE" in bar.domain_label.text()
    assert "90" in bar.levels_label.text()


def test_config_bar_change_button_emits_signal(qapp, qtbot):
    bar = ConfigBar()
    qtbot.addWidget(bar)
    with qtbot.waitSignal(bar.changeRequested, timeout=1000):
        bar.change_button.click()


def test_config_bar_missing_config_shows_honest_placeholder(qapp, qtbot):
    bar = ConfigBar()
    qtbot.addWidget(bar)
    assert "NOT_CONFIGURED_NO_RUN_SELECTED" in bar.model_label.text()
