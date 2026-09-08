"""
Tests for acf.awci.method_comparison - real Physics/Statistical/ML/
Hybrid prediction-method comparison (docs/ACF_MASTER_PROMPT.md section
41). This session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found no such comparison framework
existed anywhere in this codebase.

Cases/observations here are clearly-labeled synthetic example data
(the same honest convention used throughout this project's own test
suite) - this module's own docstring discloses that no real observed-
AWCI dataset exists anywhere in this codebase (sections 36/37 of the
same audit both confirmed absent).
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.method_comparison import (
    ClimatologicalBaselineMethod,
    MethodCategory,
    NotYetImplementedMethod,
    PhysicsBasedMethod,
    compare_methods,
)
from acf.awci.normalizer import Normalizer
from acf.verification.nwp_metrics import NWPVerificationMetrics

_CASES = [
    {"temperature": 300.0, "wind_speed": 10.0, "cape": 500.0, "altitude": 200.0},
    {"temperature": 310.0, "wind_speed": 35.0, "cape": 3000.0, "altitude": 1500.0},
    {"temperature": 295.0, "wind_speed": 5.0, "cape": 100.0, "altitude": 50.0},
]
_OBSERVATIONS = [20.0, 75.0, 10.0]  # real AWCI-scale reference values, clearly synthetic example data
_WIND_CLIMATOLOGY = [1.0, 5.0, 10.0, 15.0, 20.0, 25.0, 35.0, 45.0]


def test_physics_based_method_matches_a_direct_awcicalculator_call():
    method = PhysicsBasedMethod()
    for case in _CASES:
        expected = AWCICalculator().calculate(dict(case))["awci"]
        assert method.predict(dict(case)) == expected


def test_physics_based_method_is_correctly_categorized():
    assert PhysicsBasedMethod().category == MethodCategory.PHYSICS_BASED


def test_physics_based_method_uses_a_real_custom_calculator_when_supplied():
    custom = AWCICalculator(weights={"dynamic": 1.0})
    method = PhysicsBasedMethod(calculator=custom)
    case = dict(_CASES[0])
    assert method.predict(case) == custom.calculate(case)["awci"]
    assert method.predict(case) != AWCICalculator().calculate(case)["awci"]


def test_climatological_baseline_matches_a_direct_normalize_percentile_call():
    method = ClimatologicalBaselineMethod("wind_speed", _WIND_CLIMATOLOGY)
    for case in _CASES:
        expected = Normalizer.normalize_percentile(case["wind_speed"], _WIND_CLIMATOLOGY) * 100.0
        assert method.predict(dict(case)) == expected


def test_climatological_baseline_is_correctly_categorized():
    method = ClimatologicalBaselineMethod("wind_speed", _WIND_CLIMATOLOGY)
    assert method.category == MethodCategory.STATISTICAL


def test_climatological_baseline_raises_a_real_error_for_a_missing_variable():
    method = ClimatologicalBaselineMethod("cape", [100.0, 500.0])
    with pytest.raises(KeyError, match="cape"):
        method.predict({"wind_speed": 10.0})


def test_not_yet_implemented_method_raises_rather_than_fabricating_a_prediction():
    method = NotYetImplementedMethod(MethodCategory.MACHINE_LEARNING, "Some future ML model")
    with pytest.raises(NotImplementedError, match="Some future ML model"):
        method.predict(dict(_CASES[0]))


def test_not_yet_implemented_method_supports_the_hybrid_category_too():
    method = NotYetImplementedMethod(MethodCategory.HYBRID, "Some future hybrid model")
    with pytest.raises(NotImplementedError):
        method.predict(dict(_CASES[0]))


def test_not_yet_implemented_method_rejects_a_category_with_a_real_implementation():
    """A caller must use PhysicsBasedMethod/ClimatologicalBaselineMethod
    for those 2 categories, never this placeholder - even though
    nothing stops it mechanically, it's a real, deliberate usage error."""
    with pytest.raises(ValueError, match="real implementation"):
        NotYetImplementedMethod(MethodCategory.PHYSICS_BASED, "Should not be allowed")


def test_compare_methods_computes_real_metrics_matching_an_independent_call():
    physics = PhysicsBasedMethod()
    statistical = ClimatologicalBaselineMethod("wind_speed", _WIND_CLIMATOLOGY)

    result = compare_methods([physics, statistical], _CASES, _OBSERVATIONS)

    assert set(result.keys()) == {physics.name, statistical.name}
    physics_predictions = [physics.predict(dict(c)) for c in _CASES]
    expected_physics_metrics = NWPVerificationMetrics.evaluate_all(physics_predictions, _OBSERVATIONS, 50.0)
    assert result[physics.name]["rmse"] == expected_physics_metrics["rmse"]
    assert result[physics.name]["category"] == "physics_based"
    assert result[statistical.name]["category"] == "statistical"


def test_compare_methods_uses_a_real_default_threshold_matching_awci_moderate_band():
    physics = PhysicsBasedMethod()
    result_default = compare_methods([physics], _CASES, _OBSERVATIONS)
    result_explicit_50 = compare_methods([physics], _CASES, _OBSERVATIONS, threshold=50.0)
    assert result_default[physics.name]["pod"] == result_explicit_50[physics.name]["pod"]


def test_compare_methods_propagates_a_placeholder_methods_real_error():
    """A NotYetImplementedMethod included in a real comparison must
    genuinely fail the comparison, never be silently skipped or
    contribute a fabricated 0.0."""
    placeholder = NotYetImplementedMethod(MethodCategory.MACHINE_LEARNING, "Unbuilt ML model")
    with pytest.raises(NotImplementedError):
        compare_methods([placeholder], _CASES, _OBSERVATIONS)


def test_compare_methods_rejects_a_length_mismatch():
    physics = PhysicsBasedMethod()
    with pytest.raises(ValueError, match="same length"):
        compare_methods([physics], _CASES, _OBSERVATIONS[:2])


def test_compare_methods_with_zero_methods_returns_an_empty_result():
    assert compare_methods([], _CASES, _OBSERVATIONS) == {}
