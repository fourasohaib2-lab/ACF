"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_multimodel.ACFMultiModelLabPanel -
the real on-demand raw per-model comparison worker wiring.
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_multimodel import ACFMultiModelLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_with_no_result_and_disabled_display_selector(qapp):
    panel = ACFMultiModelLabPanel()
    assert panel._result is None
    assert panel.display_selector.isEnabled() is False
    assert "Not yet computed" in panel.status_label.text()


def test_model_selectors_list_the_real_model_configs(qapp):
    from acf.forecast.engine import MODEL_CONFIGS

    panel = ACFMultiModelLabPanel()
    names_a = {panel.model_a_selector.itemText(i) for i in range(panel.model_a_selector.count())}
    names_b = {panel.model_b_selector.itemText(i) for i in range(panel.model_b_selector.count())}
    assert names_a == set(MODEL_CONFIGS.keys())
    assert names_b == set(MODEL_CONFIGS.keys())


def test_picking_the_same_model_twice_reports_an_honest_error(qapp):
    panel = ACFMultiModelLabPanel()
    panel.model_a_selector.setCurrentText("ARPEGE")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel._start_comparison()

    assert "different real models" in panel.status_label.text()


def test_clicking_compare_genuinely_runs_off_thread_and_populates_the_map(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt
    event loop path, not a direct call - same discipline as this
    codebase's other real-worker tests."""
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel.run_button.click()

    qtbot.waitUntil(lambda: panel._result is not None, timeout=60000)
    assert panel.display_selector.isEnabled() is True
    assert "✅" in panel.status_label.text()
    assert panel.map_panel.status()["has_contour"] is True


def test_switching_display_choice_redraws_with_different_real_fields(qtbot):
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._result is not None, timeout=60000)

    panel.display_selector.setCurrentText("Model A field")
    title_a = panel.map_panel._title
    panel.display_selector.setCurrentText("Difference (A − B)")
    title_diff = panel.map_panel._title

    assert title_a != title_diff
    assert "−" in title_diff


def test_difference_field_is_the_real_elementwise_subtraction(qtbot):
    """Cross-check discipline: the displayed difference must be the
    real, literal field_a - field_b, not a separately re-derived
    statistic."""
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._result is not None, timeout=60000)
    result = panel._result
    model_a, model_b = result["models_compared"]
    expected_diff = result["per_model_field"][model_a] - result["per_model_field"][model_b]

    panel.display_selector.setCurrentText("Difference (A − B)")

    assert np.allclose(panel.map_panel._external_field[2], expected_diff)
