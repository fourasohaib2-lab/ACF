"""
Tests for acf.awci.result - the complete real AWCI result object
(docs/ACF_MASTER_PROMPT.md section 81: "Toujours conserver au minimum:
AWCI score, AWCI class, AWCI confidence, AWCI dominant factors, AWCI
interactions, AWCI model spread, AWCI quality, AWCI provenance").
This session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found model_spread/quality/provenance
existed only as 3 separate real systems, never attached to a
calculate() result.
"""

from __future__ import annotations

from datetime import UTC, datetime

from acf.awci.calculator import AWCICalculator
from acf.awci.result import build_awci_result
from acf.core.contracts.provenance import Provenance
from acf.physics_guard.variable_quality import assess_variable_quality

_DATA = {"temperature": 300.0, "wind_speed": 25.0, "cape": 2000.0, "altitude": 800.0, "confidence": 70.0}


def test_build_awci_result_carries_every_real_calculate_field_unchanged():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output)

    assert result.awci == calc_output["awci"]
    assert result.level == calc_output["level"]
    assert result.confidence == calc_output["confidence"]
    assert result.interaction_scores == calc_output["interaction_scores"]
    assert result.decomposition == calc_output["decomposition"]
    assert result.module_scores == calc_output["module_scores"]
    assert result.explanation == calc_output["explanation"]
    assert result.physical_score == calc_output["physical_score"]
    assert result.forecast_score == calc_output["forecast_score"]


def test_dominant_factors_matches_the_real_top_of_the_explanation():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output)

    expected = [line.split(" : ")[0] for line in calc_output["explanation"][:3]]
    assert result.dominant_factors == expected


def test_max_dominant_factors_is_respected():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output, max_dominant_factors=1)
    assert len(result.dominant_factors) <= 1


def test_optional_fields_default_to_none_never_fabricated():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output)

    assert result.model_spread is None
    assert result.quality is None
    assert result.provenance is None


def test_real_provenance_attaches_unchanged():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    provenance = Provenance(generator="AWCICalculator", algorithm_version="ARPEGE", science_version="1.0")

    result = build_awci_result(calc_output, provenance=provenance)

    assert result.provenance is provenance
    assert result.provenance.generator == "AWCICalculator"


def test_real_quality_attaches_unchanged():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    quality = assess_variable_quality({"air_temperature": 300.0}, expected_variables=["air_temperature"])

    result = build_awci_result(calc_output, quality=quality)

    assert result.quality is quality
    assert result.quality["air_temperature"].status == "VALID"


def test_real_model_spread_attaches_unchanged():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    model_spread = {"per_model_value": {"ARPEGE": 290.0, "ALADIN": 291.0}, "disagreement_spread": 0.5}

    result = build_awci_result(calc_output, model_spread=model_spread)

    assert result.model_spread is model_spread
    assert result.model_spread["disagreement_spread"] == 0.5


def test_all_three_optional_fields_attach_together():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    provenance = Provenance(generator="test", created_at=datetime(2026, 9, 3, tzinfo=UTC))
    quality = assess_variable_quality({"wind_speed": 25.0}, expected_variables=["wind_speed"])
    model_spread = {"disagreement_spread": 1.2}

    result = build_awci_result(calc_output, model_spread=model_spread, quality=quality, provenance=provenance)

    assert result.provenance is provenance
    assert result.quality is quality
    assert result.model_spread is model_spread
    # Real base fields are still correctly assembled alongside the optional ones.
    assert result.awci == calc_output["awci"]


def test_build_awci_result_never_mutates_the_original_calculate_output():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    original = dict(calc_output)
    build_awci_result(calc_output)
    assert calc_output == original


# ---------------------------------------- drill-down chain (§26/§53)


def test_drill_down_fields_default_to_none_never_fabricated():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output)
    assert result.raw_variables is None
    assert result.lead_time_hours is None
    assert result.vertical_level is None


def test_drill_down_fields_attach_unchanged():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output, raw_variables=dict(_DATA), lead_time_hours=6.5, vertical_level=3)
    assert result.raw_variables == _DATA
    assert result.lead_time_hours == 6.5
    assert result.vertical_level == 3


def test_trace_chain_has_exactly_the_8_real_links_sections_26_53_name():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output)
    chain = result.trace_chain()
    assert len(chain) == 8
    labels = [line.split(":")[0] for line in chain]
    assert labels == [
        "Score",
        "Contributions",
        "Variables",
        "Diagnostics (module scores)",
        "Données sources",
        "Modèle",
        "Échéance",
        "Niveau vertical",
    ]


def test_trace_chain_shows_not_available_for_unsupplied_links_not_silently_skipped():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    result = build_awci_result(calc_output)  # nothing optional supplied
    chain = result.trace_chain()
    assert "not available" in chain[2]  # Variables
    assert "not available" in chain[4]  # Données sources
    assert "not available" in chain[5]  # Modèle
    assert "not available" in chain[6]  # Échéance
    assert "not available" in chain[7]  # Niveau vertical


def test_trace_chain_shows_real_supplied_values():
    calc_output = AWCICalculator().calculate(dict(_DATA))
    provenance = Provenance(
        generator="test", algorithm_version="ARPEGE", input_files=["metar_LFPG_2026090312.txt"]
    )
    result = build_awci_result(
        calc_output,
        provenance=provenance,
        raw_variables=dict(_DATA),
        lead_time_hours=12.0,
        vertical_level=2,
    )

    chain = result.trace_chain()

    assert "ARPEGE" in chain[5]  # Modèle
    assert "metar_LFPG_2026090312.txt" in chain[4]  # Données sources
    assert "12.00h" in chain[6]  # Échéance
    assert "2" in chain[7]  # Niveau vertical
    assert str(_DATA) == chain[2].split("Variables: ")[1]  # Variables, exact real dict
