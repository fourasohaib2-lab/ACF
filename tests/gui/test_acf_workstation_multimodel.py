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


# ------------------------------------------------------- weighted fusion (2026-09-06)


def test_display_selector_lists_the_fusion_choices(qapp):
    panel = ACFMultiModelLabPanel()
    items = {panel.display_selector.itemText(i) for i in range(panel.display_selector.count())}
    assert "Weighted Fusion (A+B)" in items
    assert "Fusion Spread (A vs B)" in items


def test_picking_the_same_model_twice_reports_an_honest_fusion_error(qapp):
    panel = ACFMultiModelLabPanel()
    panel.model_a_selector.setCurrentText("ARPEGE")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel._start_fusion()

    assert "different real models" in panel.status_label.text()
    assert panel._fusion_result is None


def test_clicking_weighted_fusion_genuinely_runs_off_thread_and_populates_the_map(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt
    event loop path, same discipline as the comparison button's own test."""
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel.fusion_button.click()

    qtbot.waitUntil(lambda: panel._fusion_result is not None, timeout=60000)
    assert panel.display_selector.isEnabled() is True
    assert "✅" in panel.status_label.text()
    assert "weights" in panel.status_label.text()
    assert panel.map_panel.status()["has_contour"] is True


def test_fusion_result_is_genuinely_delegated_to_the_real_awci_fusion_module(qtbot):
    """Cross-check discipline: the panel's own fusion result must equal
    a fresh, independent direct call to the real underlying function
    with the same real inputs - never a separately re-derived field."""
    from acf.awci.multi_model_fusion import compute_real_multi_model_field_fusion

    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel.fusion_button.click()
    qtbot.waitUntil(lambda: panel._fusion_result is not None, timeout=60000)

    expected = compute_real_multi_model_field_fusion(
        field_key="temperature_field", models=["ALADIN", "ARPEGE"], target_model="ARPEGE", steps=3
    )
    assert panel._fusion_result["weights"] == expected["weights"]
    assert panel._fusion_result["weight_source"] == expected["weight_source"] == "equal_weights_no_skill_history"
    assert panel._fusion_result["target_model"] == "ARPEGE"


def test_switching_to_fusion_display_redraws_with_the_real_fused_field(qtbot):
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")
    panel.fusion_button.click()
    qtbot.waitUntil(lambda: panel._fusion_result is not None, timeout=60000)

    panel.display_selector.setCurrentText("Weighted Fusion (A+B)")
    assert np.allclose(panel.map_panel._external_field[2], panel._fusion_result["fused_field"])

    panel.display_selector.setCurrentText("Fusion Spread (A vs B)")
    assert np.allclose(panel.map_panel._external_field[2], panel._fusion_result["spread_field"])


def test_weighted_fusion_is_visible_on_the_map_without_manually_reselecting_display(qtbot):
    """BUG FIX (2026-09-11, found during a full ACF Workstation rescan):
    _on_fusion_ready() called a bare _redraw(), which branches purely on
    display_selector.currentText() - left at its own default ("Model A
    field") when Weighted Fusion is clicked with no prior "Compare
    Models" run. The real, correctly-computed fusion result was then
    unreachable from the map unless the user manually reselected
    "Weighted Fusion (A+B)" from the dropdown - nothing in the UI
    prompted that. This is the exact real-world path (fusion clicked
    FIRST, no comparison ever run) the earlier fusion tests never
    exercised, since they only ever asserted the result was computed,
    not that it was actually drawn without extra manual steps."""
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel.fusion_button.click()
    qtbot.waitUntil(lambda: panel._fusion_result is not None, timeout=60000)

    assert panel.display_selector.currentText() == "Weighted Fusion (A+B)"
    assert np.allclose(panel.map_panel._external_field[2], panel._fusion_result["fused_field"])


def test_switching_back_to_comparison_display_after_fusion_still_works(qtbot):
    """Both real result states (comparison and fusion) coexist independently in the same panel."""
    panel = ACFMultiModelLabPanel()
    qtbot.addWidget(panel)
    panel.model_a_selector.setCurrentText("ALADIN")
    panel.model_b_selector.setCurrentText("ARPEGE")

    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._result is not None, timeout=60000)
    panel.fusion_button.click()
    qtbot.waitUntil(lambda: panel._fusion_result is not None, timeout=60000)

    panel.display_selector.setCurrentText("Difference (A − B)")
    expected_diff = (
        panel._result["per_model_field"]["ALADIN"] - panel._result["per_model_field"]["ARPEGE"]
    )
    assert np.allclose(panel.map_panel._external_field[2], expected_diff)
