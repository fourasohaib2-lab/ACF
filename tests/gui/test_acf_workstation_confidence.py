"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_confidence.ACFConfidenceLabPanel -
the real on-demand full-grid multi-model disagreement worker wiring.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_confidence import ACFConfidenceLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_with_no_result_and_disabled_variable_selector(qapp):
    panel = ACFConfidenceLabPanel()
    assert panel._result is None
    assert panel.variable_selector.isEnabled() is False
    assert "Not yet computed" in panel.status_label.text()


def test_variable_selector_lists_spread_and_mean(qapp):
    panel = ACFConfidenceLabPanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert any("spread" in n for n in names)
    assert any("mean" in n for n in names)


def test_clicking_run_genuinely_runs_off_thread_and_populates_the_map(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt
    event loop path, not a direct call - same discipline as this
    codebase's other real-worker tests."""
    panel = ACFConfidenceLabPanel()
    qtbot.addWidget(panel)

    panel.run_button.click()

    qtbot.waitUntil(lambda: panel._result is not None, timeout=60000)
    assert panel.variable_selector.isEnabled() is True
    assert "✅" in panel.status_label.text()
    assert panel.map_panel.status()["has_contour"] is True


def test_switching_variable_redraws_with_a_different_real_field(qtbot):
    panel = ACFConfidenceLabPanel()
    qtbot.addWidget(panel)
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._result is not None, timeout=60000)
    first_label = panel.map_panel._external_field_colorbar_label

    panel.variable_selector.setCurrentText("Disagreement mean")

    assert panel.map_panel._external_field_colorbar_label != first_label
    assert "mean" in panel.map_panel._external_field_colorbar_label
