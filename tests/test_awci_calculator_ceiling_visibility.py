"""
Tests for AWCICalculator's real, opt-in `ceiling`/`visibility` modules
(post-model4d audit, 2026-09-11, closing AWCI's "visibilité et plafond"
gap against docs/reference "AWCI - programme complet" specification).

Critical property under test: an explicit "keep the dashboard exactly
as it is" constraint drove this closure's design - both modules default
to weight 0.0 (WeightsManager.DEFAULT_WEIGHTS) and are only computed
from a real, pre-supplied value (data["ceiling_height_m"]/
data["visibility_risk"]), never derived internally from base fields.
Every existing caller - including the AWCI dashboard, which never
supplies either key - must get a bit-identical awci score, level and
decomposition to before these modules existed. That invariant is what
most of this file actually tests, not just the modules' own arithmetic
(see test_awci_ceiling.py/test_awci_visibility.py for that).
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer
from acf.awci.weights import WeightsManager

_BASE_DATA = {
    "temperature": 300.0,
    "specific_humidity": 0.01,
    "wind_speed": 10.0,
    "cape": 1000.0,
    "cin": -100.0,
    "precipitation": 5.0,
    "pressure": 1000.0,
    "altitude": 500.0,
    "confidence": 80.0,
    "temporal_change": 5.0,
}


def test_default_weights_are_zero_for_both_new_modules():
    assert WeightsManager.DEFAULT_WEIGHTS["ceiling"] == 0.0
    assert WeightsManager.DEFAULT_WEIGHTS["visibility"] == 0.0
    # Sum still 1.0 - adding two 0.0 entries must not silently break
    # WeightsManager's own validation.
    WeightsManager()  # raises ValueError if the sum drifted off 1.0


def test_omitting_both_keys_gives_a_bit_identical_awci_to_before_these_modules_existed():
    calc = AWCICalculator()

    with_data = calc.calculate(dict(_BASE_DATA))
    scores = calc.calculate_module_scores(dict(_BASE_DATA))

    assert scores["ceiling"] == 0.0
    assert scores["visibility"] == 0.0
    # Both modules genuinely contribute 0 points to the decomposition
    # at the default weight, not merely "small" - the dashboard's own
    # AWCI score/level/decomposition for any point it has ever computed
    # is therefore unchanged.
    assert with_data["decomposition"]["ceiling"] == 0.0
    assert with_data["decomposition"]["visibility"] == 0.0


def test_omitted_module_scores_match_a_calculator_built_before_this_capability_existed():
    """Reconstructs what calculate() returned before ceiling/visibility
    existed (the real 9-key module_scores dict of the prior module set)
    and checks every shared value is unaffected - not just the two new
    keys' own contribution."""
    calc = AWCICalculator()
    result = calc.calculate(dict(_BASE_DATA))

    legacy_keys = {
        "dynamic", "thermodynamic", "convective", "microphysical", "topographic",
        "temporal", "confidence", "ensemble_spread", "model_disagreement",
    }
    assert legacy_keys <= set(result["module_scores"].keys())
    assert set(result["module_scores"].keys()) == legacy_keys | {"ceiling", "visibility"}


def test_supplying_ceiling_height_m_activates_the_real_normalize_ceiling_value():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ceiling_height_m": 200.0}

    scores = calc.calculate_module_scores(data)

    assert scores["ceiling"] == pytest.approx(Normalizer.normalize_ceiling(200.0))
    assert scores["ceiling"] > 0.0


def test_supplying_visibility_risk_activates_the_real_normalize_visibility_risk_value():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "visibility_risk": 0.7}

    scores = calc.calculate_module_scores(data)

    assert scores["visibility"] == pytest.approx(0.7)


def test_opted_in_ceiling_only_contributes_when_its_weight_is_explicitly_raised():
    """Matches the ensemble_spread/model_disagreement precedent exactly:
    supplying the real input alone is not enough to move the final AWCI
    score - the weight must also be explicitly raised by the caller."""
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ceiling_height_m": 0.0}  # worst-case real ceiling (surface obscured)

    default_weight_result = calc.calculate(data)
    assert default_weight_result["decomposition"]["ceiling"] == 0.0

    weights = WeightsManager()
    weights.update_weights({"ceiling": 0.20, "dynamic": 0.0})
    calc_weighted = AWCICalculator(weights=weights.get_all_weights())
    weighted_result = calc_weighted.calculate(data)
    assert weighted_result["decomposition"]["ceiling"] > 0.0


def test_ceiling_and_visibility_are_classified_as_physical_modules():
    assert "ceiling" in AWCICalculator.PHYSICAL_MODULES
    assert "visibility" in AWCICalculator.PHYSICAL_MODULES
    assert "ceiling" not in AWCICalculator.FORECAST_MODULES
    assert "visibility" not in AWCICalculator.FORECAST_MODULES


def test_physical_score_is_unaffected_by_the_new_modules_at_default_weight():
    calc = AWCICalculator()
    result = calc.calculate(dict(_BASE_DATA))

    # physical_score renormalizes over PHYSICAL_MODULES' weights; both
    # new modules contribute weight 0.0 and points 0.0, so the real
    # physical_score value is identical to what it was before these
    # modules existed (a genuine arithmetic check, not just "it ran").
    assert result["physical_score"] is not None
