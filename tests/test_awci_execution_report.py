"""
Tests for acf.awci.execution_report - the real per-execution report
docs/ACF_MASTER_PROMPT.md section 75 describes ("Input files: 48,
Valid: 46, Rejected: 2, Diagnostics: 123, AWCI generated: YES, Quality:
GOOD, Model spread: HIGH"). summarize_execution() is a real assembler
over an already-built acf.awci.result.AWCIResult - these tests build
real AWCIResult objects (via build_awci_result()) with hand-built
VariableQualityStatus entries (real dataclass, no computation needed)
so the exact VALID/SUSPECT/rejected counts are deterministic and
directly verifiable.
"""

from __future__ import annotations

from acf.awci.calculator import AWCICalculator
from acf.awci.execution_report import summarize_execution
from acf.awci.result import build_awci_result
from acf.physics_guard.variable_quality import VariableQualityStatus

_DATA = {"temperature": 300.0, "wind_speed": 25.0, "cape": 2000.0, "altitude": 800.0, "confidence": 70.0}


def _result(quality=None, model_spread=None):
    calc_output = AWCICalculator().calculate(dict(_DATA))
    return build_awci_result(calc_output, quality=quality, model_spread=model_spread)


def test_quality_unavailable_reports_honestly_not_fabricated():
    result = _result(quality=None)
    report = summarize_execution(result)

    assert report.quality_available is False
    assert report.quality == "UNKNOWN"
    assert report.input_variables_total == 0
    assert "not available" in "\n".join(report.render())


def test_all_valid_is_a_real_good_quality():
    quality = {
        "air_temperature": VariableQualityStatus("air_temperature", "VALID"),
        "wind_speed": VariableQualityStatus("wind_speed", "VALID"),
        "specific_humidity": VariableQualityStatus("specific_humidity", "VALID"),
    }
    report = summarize_execution(_result(quality=quality))

    assert report.quality_available is True
    assert report.input_variables_total == 3
    assert report.input_variables_valid == 3
    assert report.input_variables_rejected == 0
    assert report.input_variables_suspect == 0
    assert report.quality == "GOOD"


def test_a_minority_rejected_is_real_degraded_not_bad():
    quality = {
        "air_temperature": VariableQualityStatus("air_temperature", "VALID"),
        "wind_speed": VariableQualityStatus("wind_speed", "VALID"),
        "specific_humidity": VariableQualityStatus("specific_humidity", "VALID"),
        "cape": VariableQualityStatus("cape", "MISSING"),
    }
    report = summarize_execution(_result(quality=quality))

    assert report.input_variables_total == 4
    assert report.input_variables_valid == 3
    assert report.input_variables_rejected == 1
    assert report.quality == "DEGRADED"


def test_a_majority_rejected_is_real_bad():
    quality = {
        "air_temperature": VariableQualityStatus("air_temperature", "VALID"),
        "wind_speed": VariableQualityStatus("wind_speed", "MISSING"),
        "specific_humidity": VariableQualityStatus("specific_humidity", "INVALID"),
        "cape": VariableQualityStatus("cape", "OUT_OF_RANGE"),
    }
    report = summarize_execution(_result(quality=quality))

    assert report.input_variables_rejected == 3
    assert report.quality == "BAD"


def test_suspect_is_tracked_separately_from_rejected_and_valid():
    quality = {
        "air_temperature": VariableQualityStatus("air_temperature", "VALID"),
        "wind_speed": VariableQualityStatus("wind_speed", "SUSPECT"),
    }
    report = summarize_execution(_result(quality=quality))

    assert report.input_variables_valid == 1
    assert report.input_variables_suspect == 1
    assert report.input_variables_rejected == 0
    assert "suspect" in "\n".join(report.render())


def test_diagnostics_count_matches_the_real_module_plus_interaction_scores():
    result = _result()
    report = summarize_execution(result)
    assert report.diagnostics_count == len(result.module_scores) + len(result.interaction_scores)
    assert report.diagnostics_count > 0


def test_awci_generated_is_true_for_any_real_result():
    report = summarize_execution(_result())
    assert report.awci_generated is True
    assert "YES" in "\n".join(report.render())


def test_model_spread_unavailable_is_honest_not_fabricated():
    report = summarize_execution(_result(model_spread=None))
    assert report.model_spread_value is None
    assert report.model_spread_level is None
    assert "not available" in report.render()[-1]


def test_model_spread_shows_the_real_numeric_value_never_a_guessed_bucket_by_default():
    """No model_spread_level was supplied - summarize_execution() must
    never invent one (see module docstring: no universal scale for
    disagreement_spread)."""
    model_spread = {"disagreement_spread": 2.345, "disagreement_mean": 10.0, "field": "T"}
    report = summarize_execution(_result(model_spread=model_spread))

    assert report.model_spread_value == 2.345
    assert report.model_spread_field == "T"
    assert report.model_spread_level is None
    rendered = report.render()[-1]
    assert "not classified" in rendered
    assert "2.345" in rendered


def test_model_spread_level_is_carried_through_when_the_caller_supplies_one():
    model_spread = {"disagreement_spread": 9.1, "field": "T"}
    report = summarize_execution(_result(model_spread=model_spread), model_spread_level="HIGH")

    assert report.model_spread_level == "HIGH"
    assert "HIGH" in report.render()[-1]


def test_model_spread_level_is_ignored_when_there_is_no_real_spread_to_classify():
    """A caller-supplied level with no real model_spread attached would
    be meaningless - must not be surfaced as if it applied to something real."""
    report = summarize_execution(_result(model_spread=None), model_spread_level="HIGH")
    assert report.model_spread_level is None


def test_render_produces_the_real_section_75_field_order():
    quality = {"air_temperature": VariableQualityStatus("air_temperature", "VALID")}
    report = summarize_execution(_result(quality=quality))
    lines = report.render()
    labels = [line.split(":")[0] for line in lines]
    assert labels == ["Input variables", "Valid", "Rejected", "Diagnostics", "AWCI generated", "Quality", "Model spread"]
