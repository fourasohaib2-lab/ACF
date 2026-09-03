"""
Tests for acf.gui.dashboard.awci_vertical_profile - the real
click-to-select-level interaction (docs/ACF_MASTER_PROMPT.md §51,
priority freely chosen: "suit ton jugement") and the real per-level
module-score breakdown dialog it opens.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_vertical_profile import AWCIVerticalProfile, AWCIVerticalProfileLevelDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _click_at(widget, x, y):
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, QPointF(x, y), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
    )
    widget.mousePressEvent(event)


def test_bar_geometry_is_populated_after_a_real_paint(qapp):
    widget = AWCIVerticalProfile()
    widget.resize(400, 300)
    widget.set_profile({"Surface": 20.0, "850 hPa": 30.0, "FL180": 40.0})
    widget.repaint()

    assert len(widget._bar_geometry) == 3
    labels = [g[0] for g in widget._bar_geometry]
    assert labels == ["Surface", "850 hPa", "FL180"]


def test_clicking_a_real_bar_emits_levelclicked_with_its_label(qapp):
    widget = AWCIVerticalProfile()
    widget.resize(400, 300)
    widget.set_profile({"Surface": 20.0, "850 hPa": 30.0, "FL180": 40.0})
    widget.repaint()

    received = []
    widget.levelClicked.connect(received.append)

    level, x, bar_width = widget._bar_geometry[1]  # "850 hPa"
    _click_at(widget, x + bar_width / 2, 100)

    assert received == ["850 hPa"]


def test_clicking_outside_any_bar_emits_nothing(qapp):
    widget = AWCIVerticalProfile()
    widget.resize(400, 300)
    widget.set_profile({"Surface": 20.0, "850 hPa": 30.0})
    widget.repaint()

    received = []
    widget.levelClicked.connect(received.append)

    _click_at(widget, 2, 2)  # top-left corner, real margin area, no bar there

    assert received == []


def test_clicking_with_no_profile_does_not_raise(qapp):
    widget = AWCIVerticalProfile()
    widget.resize(400, 300)
    widget.repaint()

    _click_at(widget, 50, 50)  # must not raise


# --------------------------------------------------- AWCIVerticalProfileLevelDialog


def test_level_dialog_shows_the_real_composite_score_and_split(qapp):
    dialog = AWCIVerticalProfileLevelDialog()
    result = {
        "awci": 42.3,
        "level": "Moderate",
        "physical_score": 38.0,
        "forecast_score": 46.5,
        "module_scores": {
            "dynamic": 10.0, "thermodynamic": 20.0, "convective": 30.0,
            "microphysical": 40.0, "topographic": 50.0, "temporal": 60.0, "confidence": 70.0,
        },
    }

    dialog.show_detail("FL300", 300.9, result)

    assert "FL300" in dialog._title_label.text()
    assert "300" in dialog._title_label.text()
    assert "42.3" in dialog._score_label.text()
    assert "Moderate" in dialog._score_label.text()
    assert "38.0" in dialog._split_label.text()
    assert "46.5" in dialog._split_label.text()


def test_level_dialog_shows_every_real_module_score(qapp):
    dialog = AWCIVerticalProfileLevelDialog()
    module_scores = {
        "dynamic": 11.0, "thermodynamic": 22.0, "convective": 33.0,
        "microphysical": 44.0, "topographic": 55.0, "temporal": 66.0, "confidence": 77.0,
    }
    result = {"awci": 50.0, "level": "High", "physical_score": None, "forecast_score": None, "module_scores": module_scores}

    dialog.show_detail("850 hPa", 850.0, result)

    for key, value in module_scores.items():
        assert f"{value:.1f}" in dialog._module_rows[key].text()


def test_level_dialog_shows_an_em_dash_for_a_real_undefined_split(qapp):
    dialog = AWCIVerticalProfileLevelDialog()
    result = {"awci": 20.0, "level": "Low", "physical_score": None, "forecast_score": None, "module_scores": {}}

    dialog.show_detail("Surface", 1013.25, result)

    assert "—" in dialog._split_label.text()
