"""
Tests for acf.gui.dashboard.acf_workstation_thumbnail_strip.
ACFVariableThumbnailStrip - the real, lightweight small-multiple
preview row (Phase 37, 2026-09-05).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_thumbnail_strip import ACFVariableThumbnailStrip


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_with_no_real_field_rendered(qapp):
    strip = ACFVariableThumbnailStrip(["A", "B"])
    assert strip.status() == {"variables": ["A", "B"], "rendered": []}


def test_set_field_marks_that_variable_rendered(qapp):
    strip = ACFVariableThumbnailStrip(["A", "B"])
    field = np.random.default_rng(0).normal(size=(5, 5))

    strip.set_field("A", field, cmap="viridis", vmin=None, vmax=None)

    assert strip.status()["rendered"] == ["A"]


def test_set_field_rejects_an_unknown_variable(qapp):
    strip = ACFVariableThumbnailStrip(["A"])
    with pytest.raises(ValueError, match="Unknown real thumbnail variable"):
        strip.set_field("Z", np.zeros((2, 2)), cmap="viridis", vmin=None, vmax=None)


def test_clicking_a_thumbnail_emits_its_real_variable_name(qapp):
    strip = ACFVariableThumbnailStrip(["A", "B"])
    received = []
    strip.variableSelected.connect(received.append)

    strip._thumbnails["B"].clicked.emit()

    assert received == ["B"]


def test_set_label_overrides_the_displayed_text(qapp):
    strip = ACFVariableThumbnailStrip(["A", "B"])

    strip.set_label("A", "T+3h")

    assert strip._thumbnails["A"].label_widget.text() == "T+3h"
    assert strip._thumbnails["B"].label_widget.text() == "B"  # untouched


def test_set_label_rejects_an_unknown_variable(qapp):
    strip = ACFVariableThumbnailStrip(["A"])
    with pytest.raises(ValueError, match="Unknown real thumbnail variable"):
        strip.set_label("Z", "T+3h")


def test_set_selected_highlights_at_most_one_real_thumbnail(qapp):
    strip = ACFVariableThumbnailStrip(["A", "B"])

    strip.set_selected("A")
    assert strip._thumbnails["A"].styleSheet() != ""
    assert strip._thumbnails["B"].styleSheet() == ""

    strip.set_selected("B")
    assert strip._thumbnails["A"].styleSheet() == ""
    assert strip._thumbnails["B"].styleSheet() != ""

    strip.set_selected(None)
    assert strip._thumbnails["A"].styleSheet() == ""
    assert strip._thumbnails["B"].styleSheet() == ""
