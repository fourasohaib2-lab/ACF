"""
Tests for AWCICalculator's opt-in climatological-percentile
normalization (docs/ACF_MASTER_PROMPT.md section 20: naive min-max
normalization "peut être scientifiquement mauvaise" - percentile rank
within a real climatological sample is one of the alternatives the
section explicitly asks to be studied). Every distribution here comes
from a real, caller-supplied climatological sample - never a fabricated
parametric assumption.
"""

from __future__ import annotations

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer

_BASE_DATA = {"temperature": 290.0, "wind_speed": 10.0, "cape": 1000.0}


def test_without_climatology_behavior_is_bit_identical_to_before():
    """Omitting data["climatology"] entirely must be zero behavior
    change - the exact same naive min-max path as before this feature
    existed."""
    calc = AWCICalculator()
    with_key_absent = calc.calculate_module_scores(dict(_BASE_DATA))
    with_key_none = calc.calculate_module_scores({**_BASE_DATA, "climatology": None})
    with_key_empty = calc.calculate_module_scores({**_BASE_DATA, "climatology": {}})
    assert with_key_absent == with_key_none == with_key_empty


def test_climatology_for_one_variable_only_changes_that_variables_module():
    calc = AWCICalculator()
    naive = calc.calculate_module_scores(dict(_BASE_DATA))

    # A climatology sample where the real wind_speed=10.0 sits at a very
    # different percentile than the naive 10/50=0.2 fixed-range score.
    wind_climatology = {"wind_speed": [1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 40.0, 45.0, 48.0, 49.0]}
    with_clim = calc.calculate_module_scores({**_BASE_DATA, "climatology": wind_climatology})

    assert with_clim["dynamic"] != naive["dynamic"]
    # Every other module (no climatology supplied for those variables) is untouched.
    for key in ("thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence"):
        assert with_clim[key] == naive[key]


def test_dynamic_module_matches_an_independent_normalize_percentile_call():
    calc = AWCICalculator()
    wind_climatology = {"wind_speed": [1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 40.0, 45.0, 48.0, 49.0]}
    result = calc.calculate_module_scores({**_BASE_DATA, "climatology": wind_climatology})

    expected = Normalizer.normalize_percentile(_BASE_DATA["wind_speed"], wind_climatology["wind_speed"])
    assert result["dynamic"] == expected


def test_thermodynamic_module_combines_two_independently_normalized_climatologies():
    calc = AWCICalculator()
    data = {
        **_BASE_DATA,
        "specific_humidity": 0.01,
        "climatology": {
            "temperature": [280.0, 285.0, 288.0, 290.0, 295.0, 300.0],
            "specific_humidity": [0.001, 0.005, 0.01, 0.015, 0.02, 0.025],
        },
    }
    result = calc.calculate_module_scores(data)

    expected_temp = Normalizer.normalize_percentile(290.0, data["climatology"]["temperature"])
    expected_hum = Normalizer.normalize_percentile(0.01, data["climatology"]["specific_humidity"])
    assert result["thermodynamic"] == 0.5 * expected_temp + 0.5 * expected_hum


def test_convective_module_uses_climatology_independently_for_cape_and_cin():
    calc = AWCICalculator()
    data = {
        **_BASE_DATA,
        "cin": -50.0,
        "climatology": {
            "cape": [0.0, 500.0, 1000.0, 1500.0, 2500.0, 4000.0],
            "cin": [-200.0, -100.0, -50.0, -10.0, 0.0],
        },
    }
    result = calc.calculate_module_scores(data)

    expected_cape = Normalizer.normalize_percentile(1000.0, data["climatology"]["cape"])
    expected_cin = Normalizer.normalize_percentile(-50.0, data["climatology"]["cin"])
    assert result["convective"] == 0.7 * expected_cape + 0.3 * expected_cin


def test_microphysical_module_uses_precipitation_climatology():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "precipitation": 12.0, "climatology": {"precipitation": [0.0, 2.0, 5.0, 10.0, 20.0, 40.0]}}
    result = calc.calculate_module_scores(data)

    expected = Normalizer.normalize_percentile(12.0, data["climatology"]["precipitation"])
    assert result["microphysical"] == expected


def test_full_calculate_still_returns_a_coherent_score_with_climatology():
    """The top-level calculate() pipeline (weighting, interactions,
    level classification) must keep working unchanged when
    climatology-based module scores feed into it."""
    calc = AWCICalculator()
    data = {**_BASE_DATA, "climatology": {"wind_speed": [1.0, 5.0, 10.0, 15.0, 20.0, 45.0]}}
    result = calc.calculate(data)
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


def test_climatology_key_not_confused_with_naive_variable_names_it_doesnt_cover():
    """Only the physical variables calculate_module_scores() actually
    documents (wind_speed/temperature/specific_humidity/cape/cin/
    precipitation) are climatology-aware - a stray key must be silently
    ignored, not raise, matching every other optional-key convention in
    this method."""
    calc = AWCICalculator()
    naive = calc.calculate_module_scores(dict(_BASE_DATA))
    with_unrelated_key = calc.calculate_module_scores({**_BASE_DATA, "climatology": {"not_a_real_variable": [1.0, 2.0]}})
    assert naive == with_unrelated_key


def test_climatology_normalization_status_is_hypothesis_and_directly_queryable():
    from acf.awci.scientific_status import ScientificStatus

    status = AWCICalculator.get_climatology_normalization_status()
    assert status.status == ScientificStatus.HYPOTHESIS


def test_climatology_normalization_status_matches_the_registry_module():
    from acf.awci.scientific_status import CLIMATOLOGY_NORMALIZATION_METHOD_STATUS

    assert AWCICalculator.get_climatology_normalization_status() is CLIMATOLOGY_NORMALIZATION_METHOD_STATUS


def test_calculate_module_scores_never_mutates_the_original_data_dict():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "climatology": {"wind_speed": [1.0, 5.0, 10.0, 15.0, 20.0]}}
    original = {**data, "climatology": dict(data["climatology"])}
    calc.calculate_module_scores(data)
    assert data == original
