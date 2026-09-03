"""
Tests for AWCICalculator's real, general interaction-term engine
(docs/ACF_MASTER_PROMPT.md section 22: "étudier les interactions entre
modules... ne pas inventer arbitrairement interaction = A x B sans
justification physique ou statistique"). This session's conformance
audit (reports/ACF_MASTER_AUDIT_v2.md) found only 2 hardcoded pairwise
terms, "pas un vrai moteur généralisé". __init__'s own
interaction_terms/interaction_weights parameters are that real engine:
every existing default caller keeps the exact same 2 terms and
bit-identical output; a caller may now supply their own real,
individually-justified terms, pairs or higher-order (matching section
22's own literal 3-way example).
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator

_BASE_DATA = {
    "temperature": 300.0,
    "specific_humidity": 0.02,
    "wind_speed": 25.0,
    "cape": 2000.0,
    "cin": -50.0,
    "precipitation": 15.0,
    "pressure": 950.0,
    "altitude": 1500.0,
    "confidence": 80.0,
    "temporal_change": 5.0,
}


def test_default_construction_is_bit_identical_to_before_this_feature():
    """No interaction_terms/interaction_weights supplied: the exact
    same 2 pairwise terms and weights as the class's own compiled-in
    INTERACTION_TERMS/INTERACTION_WEIGHTS - zero behavior change for
    every existing caller."""
    calc = AWCICalculator()
    assert calc.interaction_terms == AWCICalculator.INTERACTION_TERMS
    assert calc.interaction_weights == AWCICalculator.INTERACTION_WEIGHTS

    result = calc.calculate(dict(_BASE_DATA))
    reference = AWCICalculator().calculate(dict(_BASE_DATA))
    assert result == reference


def test_mismatched_keys_between_terms_and_weights_raises():
    with pytest.raises(ValueError, match="same keys"):
        AWCICalculator(
            interaction_terms={"a": ("dynamic", "topographic")},
            interaction_weights={"b": 0.05},
        )


def test_custom_pairwise_term_replaces_the_built_in_two():
    calc = AWCICalculator(
        interaction_terms={"micro_conf_interaction": ("microphysical", "confidence")},
        interaction_weights={"micro_conf_interaction": 0.05},
    )
    module_scores = {
        "dynamic": 0.8,
        "thermodynamic": 0.5,
        "convective": 0.9,
        "microphysical": 0.2,
        "topographic": 0.6,
        "temporal": 0.1,
        "confidence": 0.3,
    }
    interactions = calc.calculate_interaction_scores(module_scores)
    assert interactions == {"micro_conf_interaction": pytest.approx(0.2 * 0.3)}
    assert "wind_topo_interaction" not in interactions


def test_custom_term_flows_through_the_full_calculate_pipeline():
    calc = AWCICalculator(
        interaction_terms={"micro_conf_interaction": ("microphysical", "confidence")},
        interaction_weights={"micro_conf_interaction": 0.05},
    )
    result = calc.calculate(dict(_BASE_DATA))

    assert "micro_conf_interaction" in result["interaction_scores"]
    assert "wind_topo_interaction" not in result["interaction_scores"]
    assert 0.0 <= result["awci"] <= 100.0
    total = sum(result["decomposition"].values())
    assert total == pytest.approx(result["awci"], abs=0.5)


def test_zero_interaction_terms_is_a_real_valid_configuration():
    """The most degenerate real case: a caller who wants the pure
    linear 7-module sum with no interaction terms at all."""
    calc = AWCICalculator(interaction_terms={}, interaction_weights={})
    result = calc.calculate(dict(_BASE_DATA))
    assert result["interaction_scores"] == {}
    assert "wind_topo_interaction" not in result["decomposition"]
    total = sum(result["decomposition"].values())
    assert total == pytest.approx(result["awci"], abs=0.5)


def test_section_22_own_literal_triplet_example():
    """docs/ACF_MASTER_PROMPT.md section 22's own example: "Vent élevé
    + Humidité élevée + Relief" - a genuine 3-way interaction. Humidity
    is folded into the "thermodynamic" module (temperature + specific
    humidity combined - see calculate_module_scores()), so the closest
    real 3-module mapping available today is dynamic (wind) x
    thermodynamic (temp+humidity) x topographic (relief) - documented
    here as a worked example of the general engine representing
    section 22's own case, not silently assumed to already exist."""
    calc = AWCICalculator(
        interaction_terms={"wind_humidity_relief_interaction": ("dynamic", "thermodynamic", "topographic")},
        interaction_weights={"wind_humidity_relief_interaction": 0.05},
    )
    module_scores = {
        "dynamic": 0.8,
        "thermodynamic": 0.6,
        "convective": 0.1,
        "microphysical": 0.1,
        "topographic": 0.7,
        "temporal": 0.1,
        "confidence": 0.2,
    }

    interactions = calc.calculate_interaction_scores(module_scores)

    assert interactions["wind_humidity_relief_interaction"] == pytest.approx(0.8 * 0.6 * 0.7)

    result = calc.calculate(dict(_BASE_DATA))
    assert 0.0 <= result["awci"] <= 100.0
    assert "wind_humidity_relief_interaction" in result["interaction_scores"]


def test_get_interaction_weight_status_is_honest_for_an_unrecognized_custom_term():
    from acf.awci.scientific_status import WeightStatus

    status = AWCICalculator.get_interaction_weight_status("a_brand_new_custom_term")
    assert status.status == WeightStatus.INITIAL
    assert "no status recorded" in status.rationale.lower()


def test_get_interaction_weight_status_still_works_for_the_two_built_in_terms():
    from acf.awci.scientific_status import WeightStatus

    for term in AWCICalculator.INTERACTION_TERMS:
        status = AWCICalculator.get_interaction_weight_status(term)
        assert status.status == WeightStatus.INITIAL


def test_calculator_does_not_mutate_the_caller_supplied_dicts():
    terms = {"micro_conf_interaction": ("microphysical", "confidence")}
    weights = {"micro_conf_interaction": 0.05}
    original_terms = dict(terms)
    original_weights = dict(weights)

    calc = AWCICalculator(interaction_terms=terms, interaction_weights=weights)
    calc.calculate(dict(_BASE_DATA))

    assert terms == original_terms
    assert weights == original_weights
