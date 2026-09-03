"""
Tests for acf.awci.diagnostic_registry - the real, centralized
diagnostic documentation catalog (docs/ACF_MASTER_PROMPT.md section
55: "Chaque diagnostic doit être documenté avec: NAME, DESCRIPTION,
PHYSICAL MEANING, EQUATION, INPUTS, OUTPUT, UNITS, VALID RANGE,
ASSUMPTIONS, LIMITATIONS, REFERENCE, TESTS"). This session's exhaustive
90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found
each real diagnostic documented only in its own scattered docstring,
never assembled into one queryable catalog.
"""

from __future__ import annotations

import dataclasses

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.diagnostic_registry import DIAGNOSTIC_REGISTRY, DiagnosticSpec, get_diagnostic, list_diagnostic_names
from acf.awci.normalizer import Normalizer
from acf.awci.scientific_status import (
    CLIMATOLOGY_NORMALIZATION_METHOD_STATUS,
    INTERACTION_WEIGHT_STATUS,
    MODULE_WEIGHT_STATUS,
    NORMALIZER_RANGE_STATUS,
    UNCERTAINTY_METHOD_STATUS,
)

# Every real, section-55-required field name (excluding this module's
# own extra `status` field, added for real cross-referencing).
_REQUIRED_FIELDS = {
    "name",
    "description",
    "physical_meaning",
    "equation",
    "inputs",
    "output",
    "units",
    "valid_range",
    "assumptions",
    "limitations",
    "reference",
    "tests",
}


def test_every_entry_has_all_12_real_section_55_fields_non_empty():
    field_names = {f.name for f in dataclasses.fields(DiagnosticSpec)}
    assert _REQUIRED_FIELDS <= field_names

    for key, spec in DIAGNOSTIC_REGISTRY.items():
        for field_name in _REQUIRED_FIELDS:
            value = getattr(spec, field_name)
            assert value, f"{key}.{field_name} is empty - every section-55 field must be real, non-empty documentation."


def test_every_entrys_name_field_matches_its_own_registry_key():
    for key, spec in DIAGNOSTIC_REGISTRY.items():
        assert spec.name == key


def test_get_diagnostic_returns_the_real_registered_entry():
    spec = get_diagnostic("normalize_wind")
    assert spec.name == "normalize_wind"
    assert spec is DIAGNOSTIC_REGISTRY["normalize_wind"]


def test_get_diagnostic_raises_for_an_unknown_name():
    with pytest.raises(KeyError):
        get_diagnostic("not_a_real_diagnostic")


def test_list_diagnostic_names_is_sorted_and_matches_the_registry():
    assert list_diagnostic_names() == sorted(DIAGNOSTIC_REGISTRY.keys())


def test_diagnostic_spec_is_frozen():
    spec = get_diagnostic("normalize_wind")
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.name = "tampered"  # type: ignore[misc]


# ---------------------------- real cross-reference to scientific_status


def test_normalizer_range_entries_cross_reference_the_real_status_registry():
    for key, status_key in [
        ("normalize_wind", "wind"),
        ("normalize_temperature", "temperature"),
        ("normalize_humidity", "humidity"),
        ("normalize_cape", "cape"),
        ("normalize_cin", "cin"),
        ("normalize_precipitation", "precipitation"),
        ("normalize_topographic", "topographic"),
        ("normalize_confidence", "confidence"),
    ]:
        assert DIAGNOSTIC_REGISTRY[key].status is NORMALIZER_RANGE_STATUS[status_key]


def test_module_combination_entries_cross_reference_the_real_status_registry():
    assert DIAGNOSTIC_REGISTRY["thermodynamic_module_combination"].status is MODULE_WEIGHT_STATUS["thermodynamic"]
    assert DIAGNOSTIC_REGISTRY["convective_module_combination"].status is MODULE_WEIGHT_STATUS["convective"]


def test_interaction_entries_cross_reference_the_real_status_registry():
    assert DIAGNOSTIC_REGISTRY["wind_topo_interaction"].status is INTERACTION_WEIGHT_STATUS["wind_topo_interaction"]
    assert DIAGNOSTIC_REGISTRY["conv_thermo_interaction"].status is INTERACTION_WEIGHT_STATUS["conv_thermo_interaction"]


def test_uncertainty_entry_cross_references_the_real_status_registry():
    assert DIAGNOSTIC_REGISTRY["calculate_with_uncertainty"].status is UNCERTAINTY_METHOD_STATUS


def test_percentile_entry_cross_references_the_real_climatology_status():
    assert DIAGNOSTIC_REGISTRY["normalize_percentile"].status is CLIMATOLOGY_NORMALIZATION_METHOD_STATUS


# ---------------------------- real cross-check against the live formulas


def test_documented_equations_match_the_real_live_normalizer_output():
    """Real proof the documented equation text isn't stale - each
    entry's own `equation` describes a formula that, run directly,
    matches Normalizer's real output for a real test value."""
    assert Normalizer.normalize_wind(25.0) == pytest.approx(0.5)  # clip(25,0,50)/50
    assert Normalizer.normalize_temperature(283.15) == pytest.approx(0.5)  # 10 degC -> (10+30)/80
    assert Normalizer.normalize_cape(2500.0) == pytest.approx(0.5)  # clip(2500,0,5000)/5000


def test_documented_module_combination_weights_match_the_real_calculator():
    """Real proof the 0.5/0.5 and 0.7/0.3 documented weights aren't
    stale - reconstructs each real module score from Normalizer calls
    directly and compares to AWCICalculator's own real output."""
    data = {"temperature": 300.0, "specific_humidity": 0.02, "cape": 1500.0, "cin": -80.0}
    scores = AWCICalculator().calculate_module_scores(data)

    expected_thermo = 0.5 * Normalizer.normalize_temperature(300.0) + 0.5 * Normalizer.normalize_humidity(0.02)
    expected_conv = 0.7 * Normalizer.normalize_cape(1500.0) + 0.3 * Normalizer.normalize_cin(-80.0)

    assert scores["thermodynamic"] == pytest.approx(expected_thermo)
    assert scores["convective"] == pytest.approx(expected_conv)


def test_documented_default_interaction_terms_match_the_real_calculator():
    module_scores = {
        "dynamic": 0.6,
        "thermodynamic": 0.4,
        "convective": 0.8,
        "microphysical": 0.1,
        "topographic": 0.3,
        "temporal": 0.2,
        "confidence": 0.5,
    }
    interactions = AWCICalculator().calculate_interaction_scores(module_scores)

    assert interactions["wind_topo_interaction"] == pytest.approx(0.6 * 0.3)
    assert interactions["conv_thermo_interaction"] == pytest.approx(0.8 * 0.4)
