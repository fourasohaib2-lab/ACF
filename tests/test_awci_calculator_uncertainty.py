"""
Tests for AWCICalculator.calculate_with_uncertainty() - explicit
docs/ACF_MASTER_PROMPT.md section 64: "AWCI = 72 ± uncertainty ou
P(AWCI class)". Every distribution here must come from real per-member/
per-model realizations already supported by ensemble_spread/
model_disagreement - never a fabricated parametric assumption.
"""

from __future__ import annotations

from acf.awci.calculator import AWCICalculator

_BASE_DATA = {"temperature": 290.0, "wind_speed": 10.0, "cape": 1000.0}


def test_without_real_ensemble_data_returns_an_honest_unavailable_state():
    """docs/ACF_MASTER_PROMPT.md section 61: prefer UNKNOWN to false
    certainty - no fabricated band from confidence alone."""
    calc = AWCICalculator()
    result = calc.calculate_with_uncertainty(_BASE_DATA)
    assert result["uncertainty_available"] is False
    assert "no honest basis" in result["uncertainty_note"].lower()
    # The real point score is still computed normally.
    assert result["awci"] >= 0.0


def test_fewer_than_two_real_members_is_also_honestly_unavailable():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ensemble_members": {"cape": [1000.0]}}
    result = calc.calculate_with_uncertainty(data)
    assert result["uncertainty_available"] is False


def test_real_ensemble_disagreement_produces_a_real_nonzero_spread():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ensemble_members": {"cape": [100.0, 1000.0, 2500.0], "wind_speed": [3.0, 10.0, 22.0]}}
    result = calc.calculate_with_uncertainty(data)
    assert result["uncertainty_available"] is True
    assert result["n_realizations"] == 3
    assert result["awci_std"] > 0.0
    assert result["awci_min"] <= result["awci_mean"] <= result["awci_max"]


def test_member_scores_are_real_independent_awci_calculations():
    """Each entry in awci_member_scores must equal what calculate()
    itself would produce for that exact real substituted scenario -
    proof this is a genuine per-realization computation, not a
    shortcut approximation."""
    calc = AWCICalculator()
    cape_values = [100.0, 1000.0, 2500.0]
    data = {**_BASE_DATA, "ensemble_members": {"cape": cape_values}}
    result = calc.calculate_with_uncertainty(data)

    for i, cape in enumerate(cape_values):
        member_data = {**_BASE_DATA, "cape": cape}
        expected = calc.calculate(member_data)["awci"]
        assert result["awci_member_scores"][i] == round(expected, 1)


def test_tight_agreement_produces_a_smaller_spread_than_wide_disagreement():
    """Real physical property: real model/ensemble agreement must
    genuinely narrow the distribution relative to real disagreement -
    not a coincidence of the specific numbers chosen."""
    calc = AWCICalculator()
    agreeing = {**_BASE_DATA, "ensemble_members": {"cape": [990.0, 1000.0, 1010.0]}}
    disagreeing = {**_BASE_DATA, "ensemble_members": {"cape": [100.0, 1000.0, 2500.0]}}

    tight = calc.calculate_with_uncertainty(agreeing)
    wide = calc.calculate_with_uncertainty(disagreeing)

    assert tight["awci_std"] < wide["awci_std"]


def test_class_probabilities_are_real_empirical_fractions_summing_to_one():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ensemble_members": {"cape": [100.0, 1000.0, 2500.0, 4500.0]}}
    result = calc.calculate_with_uncertainty(data)
    total = sum(result["awci_class_probabilities"].values())
    assert abs(total - 1.0) < 1e-9


def test_class_probabilities_match_a_real_manual_count():
    calc = AWCICalculator()
    cape_values = [100.0, 1000.0, 2500.0, 4500.0]
    data = {**_BASE_DATA, "ensemble_members": {"cape": cape_values}}
    result = calc.calculate_with_uncertainty(data)

    manual_levels = [calc._get_level(calc.calculate({**_BASE_DATA, "cape": c})["awci"]) for c in cape_values]
    for level in set(manual_levels):
        expected_fraction = manual_levels.count(level) / len(manual_levels)
        assert result["awci_class_probabilities"][level] == round(expected_fraction, 3)


def test_model_realizations_alone_also_produce_a_real_distribution():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "model_realizations": {"temperature": [280.0, 300.0, 320.0]}}
    result = calc.calculate_with_uncertainty(data)
    assert result["uncertainty_available"] is True
    assert result["awci_std"] > 0.0


def test_both_ensemble_and_model_realizations_combine_without_crashing():
    calc = AWCICalculator()
    data = {
        **_BASE_DATA,
        "ensemble_members": {"cape": [500.0, 1000.0, 1500.0]},
        "model_realizations": {"temperature": [285.0, 290.0, 295.0]},
    }
    result = calc.calculate_with_uncertainty(data)
    assert result["uncertainty_available"] is True
    assert result["n_realizations"] == 3


def test_calculate_with_uncertainty_never_mutates_the_original_data_dict():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ensemble_members": {"cape": [100.0, 1000.0, 2500.0]}}
    original = dict(data)
    calc.calculate_with_uncertainty(data)
    assert data == original


def test_result_carries_the_real_method_status_when_available():
    from acf.awci.scientific_status import ScientificStatus

    calc = AWCICalculator()
    data = {**_BASE_DATA, "ensemble_members": {"cape": [100.0, 1000.0, 2500.0]}}
    result = calc.calculate_with_uncertainty(data)
    assert result["uncertainty_method_status"].status == ScientificStatus.HYPOTHESIS


def test_get_uncertainty_method_status_is_directly_queryable():
    from acf.awci.scientific_status import ScientificStatus

    status = AWCICalculator.get_uncertainty_method_status()
    assert status.status == ScientificStatus.HYPOTHESIS


def test_point_awci_in_result_matches_a_plain_calculate_call():
    """calculate_with_uncertainty() must not change the real point
    score calculate() would independently produce for the same data."""
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ensemble_members": {"cape": [100.0, 1000.0, 2500.0]}}
    with_uncertainty = calc.calculate_with_uncertainty(data)
    plain = calc.calculate(data)
    assert with_uncertainty["awci"] == plain["awci"]
