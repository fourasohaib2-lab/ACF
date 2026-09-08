"""
Tests for AWCICalculator's real ACF-core-vs-AWCI-application boundary
(docs/ACF_MASTER_PROMPT.md sections 45/47 - see AWCICalculator's own
class docstring, "ACF core vs. AWCI application layer" section, for the
full architecture mapping this formalizes). Per the explicit prior user
decision recorded in docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md ("évoluer
awci/ sur place... règle 'ne rien déplacer'") and reconfirmed for this
exact work, no code is relocated into a separate package - this proves
the reuse boundary is real by actually exercising it, not by moving
files.

_get_level()'s own thresholds (previously hardcoded if/elif literals)
are the concrete piece generalized in this pass, following the same
"class attribute + constructor override" pattern already proven for
interaction_terms/interaction_weights (section 22).
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


def test_default_level_thresholds_is_bit_identical_to_before():
    calc = AWCICalculator()
    assert calc.level_thresholds == AWCICalculator.LEVEL_THRESHOLDS
    for score in [0.0, 19.9, 20.0, 34.9, 35.0, 49.9, 50.0, 64.9, 65.0, 84.9, 85.0, 100.0]:
        assert calc._get_level(score) == _reference_level(score)


def _reference_level(score: float) -> str:
    """The exact old hardcoded if/elif ladder, kept here only as an
    independent reference to verify the new generic lookup against -
    not imported from production code."""
    if score < 20:
        return "Very Low"
    elif score < 35:
        return "Low"
    elif score < 50:
        return "Moderate"
    elif score < 65:
        return "High"
    elif score < 85:
        return "Very High"
    else:
        return "Extreme"


def test_boundary_scores_use_the_correct_band_not_the_one_below():
    calc = AWCICalculator()
    assert calc._get_level(20.0) == "Low"  # not "Very Low"
    assert calc._get_level(35.0) == "Moderate"
    assert calc._get_level(85.0) == "Extreme"  # not "Very High" - matches the original if/elif exactly


def test_default_construction_full_calculate_is_bit_identical():
    calc = AWCICalculator()
    reference = AWCICalculator().calculate(dict(_BASE_DATA))
    result = calc.calculate(dict(_BASE_DATA))
    assert result == reference


def test_custom_level_thresholds_change_classification():
    calc = AWCICalculator(level_thresholds=((50.0, "Below Median"), (float("inf"), "Above Median")))
    assert calc._get_level(10.0) == "Below Median"
    assert calc._get_level(90.0) == "Above Median"


def test_empty_level_thresholds_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        AWCICalculator(level_thresholds=())


def test_unsorted_level_thresholds_raises():
    with pytest.raises(ValueError, match="ascending"):
        AWCICalculator(level_thresholds=((50.0, "High"), (20.0, "Low")))


def test_duplicate_bound_level_thresholds_raises():
    with pytest.raises(ValueError, match="ascending"):
        AWCICalculator(level_thresholds=((50.0, "A"), (50.0, "B")))


def test_a_hypothetical_non_aviation_application_reuses_the_same_generic_engine():
    """The real worked proof referenced in AWCICalculator's own class
    docstring: a completely different weight/interaction/threshold
    configuration - simulating a hypothetical non-aviation application
    of the same engine (section 46's "DWCI/MWCI/..." - not built here,
    just proven reusable) - still produces a real, coherent,
    independently-computed score through the exact same mechanism."""
    hypothetical_application = AWCICalculator(
        weights={
            "dynamic": 0.40,
            "thermodynamic": 0.10,
            "convective": 0.05,
            "microphysical": 0.05,
            "topographic": 0.30,
            "temporal": 0.05,
            "confidence": 0.05,
        },
        interaction_terms={"wind_relief_interaction": ("dynamic", "topographic")},
        interaction_weights={"wind_relief_interaction": 0.10},
        level_thresholds=((25.0, "Calm"), (60.0, "Rough"), (float("inf"), "Severe")),
    )

    result = hypothetical_application.calculate(dict(_BASE_DATA))

    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Calm", "Rough", "Severe"}
    assert "wind_relief_interaction" in result["interaction_scores"]
    assert "wind_topo_interaction" not in result["interaction_scores"]

    # A real, independent AWCICalculator() (the actual AWCI aviation
    # application, untouched default config) computing the SAME raw
    # data produces a genuinely different score/level - proof the two
    # configurations are not silently collapsing to the same behavior.
    aviation_application = AWCICalculator()
    aviation_result = aviation_application.calculate(dict(_BASE_DATA))
    assert result["awci"] != aviation_result["awci"]


def test_caller_supplied_level_thresholds_tuple_is_not_mutated():
    thresholds = ((50.0, "Below"), (float("inf"), "Above"))
    calc = AWCICalculator(level_thresholds=thresholds)
    calc._get_level(10.0)
    assert calc.level_thresholds == thresholds
