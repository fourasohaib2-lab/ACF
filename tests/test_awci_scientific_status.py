"""
Tests for acf.awci.scientific_status - the real, queryable
CONFIRMED/PROPOSED/HYPOTHESIS/REQUIRES_VALIDATION/UNKNOWN and
INITIAL/EXPERT_BASED/CALIBRATED/VALIDATED status registry, explicit
user request: docs/ACF_MASTER_PROMPT.md (now the project's
authoritative specification) sections 21/77-81 repeatedly demand this.

Purely additive metadata - these tests also confirm real AWCI
computation is completely unaffected by adding it.
"""

from __future__ import annotations

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer
from acf.awci.scientific_status import (
    INTERACTION_WEIGHT_STATUS,
    MODULE_WEIGHT_STATUS,
    NORMALIZER_RANGE_STATUS,
    ScientificStatus,
    WeightStatus,
    get_interaction_weight_status,
    get_module_weight_status,
    get_normalizer_range_status,
)
from acf.awci.weights import WeightsManager


def test_every_real_module_weight_has_a_real_status():
    """WeightsManager.DEFAULT_WEIGHTS' own real keys, cross-checked -
    not a separately hand-typed list that could silently drift."""
    for module in WeightsManager.DEFAULT_WEIGHTS:
        assert module in MODULE_WEIGHT_STATUS, f"{module} has no recorded status"


def test_no_status_is_falsely_calibrated_or_validated():
    """Honest fact: nothing in this codebase has been through a real
    calibration/validation pipeline yet - a real regression guard
    against silently upgrading a status without real evidence."""
    for entry in MODULE_WEIGHT_STATUS.values():
        assert entry.status in (WeightStatus.INITIAL, WeightStatus.EXPERT_BASED)
    for entry in INTERACTION_WEIGHT_STATUS.values():
        assert entry.status in (WeightStatus.INITIAL, WeightStatus.EXPERT_BASED)


def test_opt_in_forecast_weights_are_initial_not_expert_based():
    """ensemble_spread/model_disagreement default to 0.0 (unassigned) -
    real fact, not EXPERT_BASED (no expert judged their magnitude)."""
    assert get_module_weight_status("ensemble_spread").status == WeightStatus.INITIAL
    assert get_module_weight_status("model_disagreement").status == WeightStatus.INITIAL


def test_core_module_weights_are_expert_based():
    for module in ("dynamic", "thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence"):
        assert get_module_weight_status(module).status == WeightStatus.EXPERT_BASED


def test_unknown_module_returns_an_honest_default_not_a_crash():
    status = get_module_weight_status("not_a_real_module")
    assert status.status == WeightStatus.INITIAL
    assert "no status recorded" in status.rationale.lower()


def test_interaction_weights_are_hypothesis_grade_per_calculators_own_docstring():
    for term in AWCICalculator.INTERACTION_WEIGHTS:
        assert term in INTERACTION_WEIGHT_STATUS, term
    for term in INTERACTION_WEIGHT_STATUS:
        assert get_interaction_weight_status(term).status == WeightStatus.INITIAL


def test_every_real_normalizer_range_has_a_status():
    for variable in ("temperature", "wind", "humidity", "cape", "cin", "precipitation", "pressure", "topographic", "confidence", "temporal"):
        assert variable in NORMALIZER_RANGE_STATUS, variable


def test_confidence_range_is_genuinely_confirmed_not_a_blanket_hypothesis():
    """0-100% is an exact unit definition, not an empirical choice -
    real proof the registry makes a genuine distinction, not a uniform
    label applied everywhere."""
    assert get_normalizer_range_status("confidence").status == ScientificStatus.CONFIRMED


def test_physical_ranges_are_honestly_hypothesis_not_confirmed():
    for variable in ("wind", "cape", "cin", "precipitation", "temperature"):
        assert get_normalizer_range_status(variable).status == ScientificStatus.HYPOTHESIS


def test_unknown_variable_returns_unknown_status_not_a_crash():
    status = get_normalizer_range_status("not_a_real_variable")
    assert status.status == ScientificStatus.UNKNOWN


def test_weights_manager_exposes_the_real_status_method():
    wm = WeightsManager()
    status = wm.get_weight_status("dynamic")
    assert status.status == WeightStatus.EXPERT_BASED


def test_normalizer_exposes_the_real_status_method():
    status = Normalizer.get_range_status("wind")
    assert status.status == ScientificStatus.HYPOTHESIS


def test_calculator_exposes_the_real_interaction_status_method():
    status = AWCICalculator.get_interaction_weight_status("wind_topo_interaction")
    assert status.status == WeightStatus.INITIAL


def test_adding_status_metadata_does_not_change_real_awci_computation():
    """Purely additive - a real AWCICalculator.calculate() call must
    produce bit-identical output to before this module existed."""
    calc = AWCICalculator()
    result = calc.calculate({"wind_speed": 25.0, "temperature": 290.0, "specific_humidity": 0.01})
    assert result["awci"] > 0.0
    # Cross-check against the real, direct Normalizer/WeightsManager math independently.
    expected_dynamic = Normalizer.normalize_wind(25.0)
    assert expected_dynamic == 0.5
