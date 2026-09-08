"""
Tests for acf.gui.esoc.panel_manager.MachineLearningPanel - the real
Model Calibration / Feature Importance / Uncertainty Quantification
panel closing the previously-empty "Machine Learning" System Explorer
category (2026-09-04, fourth of 7 ESOC categories with no real panel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.ai.uncertainty.uncertainty_engine import UncertaintyQuantificationEngine
from acf.ai.xai.feature_importance import FeatureImportanceAnalyzer
from acf.awci.scientific_status import (
    INTERACTION_WEIGHT_STATUS,
    MODULE_WEIGHT_STATUS,
    NORMALIZER_RANGE_STATUS,
)
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import MachineLearningPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_calibration_table_shows_every_real_status_entry(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = MachineLearningPanel(registry, dispatcher)

    expected_count = len(MODULE_WEIGHT_STATUS) + len(INTERACTION_WEIGHT_STATUS) + len(NORMALIZER_RANGE_STATUS)
    assert panel.calibration_table.rowCount() == expected_count
    names = {panel.calibration_table.item(row, 0).text() for row in range(panel.calibration_table.rowCount())}
    assert set(MODULE_WEIGHT_STATUS) <= names
    assert set(INTERACTION_WEIGHT_STATUS) <= names
    assert set(NORMALIZER_RANGE_STATUS) <= names


def test_calibration_table_status_matches_the_real_registry_directly(qapp):
    """Cross-check discipline: every real row's status/rationale must
    equal the real registry entry it was built from."""
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = MachineLearningPanel(registry, dispatcher)

    for row in range(panel.calibration_table.rowCount()):
        name = panel.calibration_table.item(row, 0).text()
        kind = panel.calibration_table.item(row, 1).text()
        status = panel.calibration_table.item(row, 2).text()
        if kind == "Module weight":
            assert status == MODULE_WEIGHT_STATUS[name].status.value
        elif kind == "Interaction weight":
            assert status == INTERACTION_WEIGHT_STATUS[name].status.value
        else:
            assert status == NORMALIZER_RANGE_STATUS[name].status.value


def test_calibration_table_honestly_shows_none_are_calibrated_or_validated(qapp):
    """Real, disclosed fact this codebase's own registry establishes:
    no AWCI weight/threshold has gone through a real calibration/
    validation pipeline yet - must not be silently hidden."""
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = MachineLearningPanel(registry, dispatcher)

    statuses = {panel.calibration_table.item(row, 2).text() for row in range(panel.calibration_table.rowCount())}
    assert "calibrated" not in statuses
    assert "validated" not in statuses


def test_feature_importance_shows_the_real_honest_disclosure(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = MachineLearningPanel(registry, dispatcher)

    expected = FeatureImportanceAnalyzer.compute_feature_importance()
    assert expected["is_real_data"] is False
    assert panel.feature_importance_result == expected
    assert expected["status"] in panel.feature_importance_label.text()
    assert "is_real_data=False" in panel.feature_importance_label.text()


def test_uncertainty_quant_computes_a_real_decomposition_matching_the_engine_directly(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = MachineLearningPanel(registry, dispatcher)

    panel.uq_input.setText("12.4, 13.1, 11.9, 12.8, 13.5")
    panel.uq_confidence.setCurrentText("95%")
    panel.uq_button.click()

    predictions = [12.4, 13.1, 11.9, 12.8, 13.5]
    expected = UncertaintyQuantificationEngine.decompose_uncertainty(predictions)
    ci_low, ci_high = UncertaintyQuantificationEngine.calculate_confidence_interval(
        expected["mean"], expected["total_std"], confidence_level=0.95
    )
    text = panel.uq_result.toPlainText()
    assert f"{expected['mean']:.4f}" in text
    assert f"{expected['total_std']:.4f}" in text
    assert f"{ci_low:.4f}" in text
    assert f"{ci_high:.4f}" in text


def test_uncertainty_quant_result_genuinely_changes_with_real_input(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = MachineLearningPanel(registry, dispatcher)

    panel.uq_input.setText("1.0, 1.0, 1.0")
    panel.uq_button.click()
    low_spread = panel.uq_result.toPlainText()

    panel.uq_input.setText("1.0, 50.0, 100.0")
    panel.uq_button.click()
    high_spread = panel.uq_result.toPlainText()

    assert low_spread != high_spread


def test_uncertainty_quant_honestly_rejects_non_numeric_input(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = MachineLearningPanel(registry, dispatcher)

    panel.uq_input.setText("not, a, number")
    panel.uq_button.click()

    assert "⚠" in panel.uq_result.toPlainText()


def test_uncertainty_quant_honestly_rejects_empty_input(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = MachineLearningPanel(registry, dispatcher)

    panel.uq_input.setText("")
    panel.uq_button.click()

    assert "⚠" in panel.uq_result.toPlainText()
