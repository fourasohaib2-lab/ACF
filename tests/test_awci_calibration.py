"""
Tests for acf.awci.calibration - real separation of calibration from
validation (docs/ACF_MASTER_PROMPT.md section 40: "ne jamais calibrer
et valider sur exactement les mêmes cas sans contrôle méthodologique").
This session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found no train/calibration/validation
separation existed anywhere in this codebase before this module.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.calibration import LockedModel, ValidationOverlapError, lock_calibration, validate_locked_model

_WEIGHTS = {
    "dynamic": 0.20,
    "thermodynamic": 0.25,
    "convective": 0.20,
    "microphysical": 0.15,
    "topographic": 0.10,
    "temporal": 0.05,
    "confidence": 0.05,
}
_INTERACTION_TERMS = {"wind_topo_interaction": ("dynamic", "topographic")}
_INTERACTION_WEIGHTS = {"wind_topo_interaction": 0.05}
_LEVEL_THRESHOLDS = ((20.0, "Very Low"), (50.0, "Moderate"), (float("inf"), "High"))
_CASE_IDS = {"CASE-2026-001", "CASE-2026-002", "CASE-2026-003"}
_BASE_DATA = {"temperature": 300.0, "wind_speed": 15.0, "cape": 1500.0, "altitude": 800.0}


def _locked_model(**overrides: Any) -> LockedModel:
    kwargs: dict[str, Any] = dict(
        weights=_WEIGHTS,
        interaction_terms=_INTERACTION_TERMS,
        interaction_weights=_INTERACTION_WEIGHTS,
        level_thresholds=_LEVEL_THRESHOLDS,
        calibration_version="test-2026.09",
        calibrated_on_case_ids=_CASE_IDS,
    )
    kwargs.update(overrides)
    return lock_calibration(**kwargs)


def test_lock_calibration_produces_a_real_locked_model():
    model = _locked_model()
    assert model.calibration_version == "test-2026.09"
    assert model.calibrated_on_case_ids == frozenset(_CASE_IDS)


def test_empty_case_ids_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        _locked_model(calibrated_on_case_ids=[])


def test_invalid_interaction_config_propagates_from_awcicalculator():
    """lock_calibration() reuses AWCICalculator.__init__()'s own real
    validation - never reimplements it."""
    with pytest.raises(ValueError, match="same keys"):
        _locked_model(interaction_weights={"a_different_term": 0.05})


def test_invalid_level_thresholds_propagates_from_awcicalculator():
    with pytest.raises(ValueError, match="ascending"):
        _locked_model(level_thresholds=((50.0, "High"), (20.0, "Low")))


def test_build_calculator_matches_an_independently_constructed_one():
    model = _locked_model()
    from_locked = model.build_calculator().calculate(dict(_BASE_DATA))
    independent = AWCICalculator(
        weights=_WEIGHTS,
        interaction_terms=_INTERACTION_TERMS,
        interaction_weights=_INTERACTION_WEIGHTS,
        level_thresholds=_LEVEL_THRESHOLDS,
    ).calculate(dict(_BASE_DATA))
    assert from_locked == independent


def test_locked_model_is_not_affected_by_later_mutation_of_the_original_dicts():
    weights = dict(_WEIGHTS)
    model = _locked_model(weights=weights)
    weights["dynamic"] = 0.99

    assert model.weights["dynamic"] == _WEIGHTS["dynamic"]


def test_locked_model_fields_cannot_be_reassigned():
    model = _locked_model()
    with pytest.raises(dataclasses.FrozenInstanceError):
        model.calibration_version = "tampered"  # type: ignore[misc]


def test_validate_locked_model_passes_for_a_disjoint_validation_set():
    model = _locked_model()
    validate_locked_model(model, ["CASE-2026-999", "CASE-2026-998"])  # must not raise


def test_validate_locked_model_raises_for_a_full_overlap():
    model = _locked_model()
    with pytest.raises(ValidationOverlapError) as excinfo:
        validate_locked_model(model, _CASE_IDS)
    assert "test-2026.09" in str(excinfo.value)


def test_validate_locked_model_raises_for_a_partial_overlap_and_names_only_the_overlap():
    model = _locked_model()
    with pytest.raises(ValidationOverlapError) as excinfo:
        validate_locked_model(model, ["CASE-2026-001", "CASE-2026-999"])
    assert "CASE-2026-001" in str(excinfo.value)
    assert "CASE-2026-999" not in str(excinfo.value)


def test_validate_locked_model_runs_before_any_calculation_would_be_wasted():
    """The check itself is pure and cheap - real proof it works
    standalone, without needing to build a calculator first."""
    model = _locked_model()
    with pytest.raises(ValidationOverlapError):
        validate_locked_model(model, _CASE_IDS)
    # Building a real calculator from the same model still works
    # independently afterward - the overlap check doesn't corrupt the
    # model itself.
    assert model.build_calculator().calculate(dict(_BASE_DATA))["awci"] >= 0.0
