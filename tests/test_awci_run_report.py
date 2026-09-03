"""
Tests for acf.awci.run_report - real per-run summary report (docs/
ACF_MASTER_PROMPT.md section 75). This session's exhaustive 90-section
conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found no such
report tied to a real AWCI run existed anywhere in this codebase.
"""

from __future__ import annotations

import dataclasses

import pytest

from acf.awci.run_report import build_run_report
from acf.physics_guard.variable_quality import assess_variable_quality


def test_default_report_is_honestly_empty():
    report = build_run_report()
    assert report.input_files_count == 0
    assert report.valid_count == 0
    assert report.rejected_count == 0
    assert report.diagnostics_count == 0
    assert report.awci_generated is False
    assert report.quality_status == "NOT_ASSESSED"
    assert report.model_spread is None


def test_real_counts_carry_through_unchanged():
    report = build_run_report(input_files_count=48, valid_count=46, rejected_count=2, diagnostics_count=123, awci_generated=True)
    assert report.input_files_count == 48
    assert report.valid_count == 46
    assert report.rejected_count == 2
    assert report.diagnostics_count == 123
    assert report.awci_generated is True


def test_quality_status_is_not_assessed_when_no_quality_results_supplied():
    report = build_run_report(quality_results=None)
    assert report.quality_status == "NOT_ASSESSED"

    report_empty = build_run_report(quality_results={})
    assert report_empty.quality_status == "NOT_ASSESSED"


def test_quality_status_is_pass_when_every_real_entry_is_valid():
    quality = assess_variable_quality({"air_temperature": 288.0}, expected_variables=["air_temperature"])
    report = build_run_report(quality_results=quality)
    assert report.quality_status == "PASS"


def test_quality_status_is_fail_when_at_least_one_real_entry_is_not_valid():
    quality = assess_variable_quality(
        {"air_temperature": 288.0, "wind_speed": 500.0}, expected_variables=["air_temperature", "wind_speed"]
    )
    assert quality["wind_speed"].status == "OUT_OF_RANGE"

    report = build_run_report(quality_results=quality)

    assert report.quality_status == "FAIL"


def test_model_spread_carries_through_as_a_real_numeric_value_not_binned():
    report = build_run_report(model_spread=2.3)
    assert report.model_spread == 2.3


def test_model_spread_defaults_to_none_never_fabricated():
    report = build_run_report()
    assert report.model_spread is None


def test_format_text_matches_the_real_section_75_example_format():
    report = build_run_report(
        input_files_count=48, valid_count=46, rejected_count=2, diagnostics_count=123, awci_generated=True
    )
    quality = assess_variable_quality({"air_temperature": 288.0}, expected_variables=["air_temperature"])
    report = build_run_report(
        input_files_count=48,
        valid_count=46,
        rejected_count=2,
        diagnostics_count=123,
        awci_generated=True,
        quality_results=quality,
    )

    text = report.format_text()

    assert text == (
        "Input files: 48\n"
        "Valid: 46\n"
        "Rejected: 2\n"
        "Diagnostics: 123\n"
        "AWCI generated: YES\n"
        "Quality: PASS"
    )


def test_format_text_includes_model_spread_only_when_supplied():
    without_spread = build_run_report().format_text()
    assert "Model spread" not in without_spread

    with_spread = build_run_report(model_spread=1.5).format_text()
    assert "Model spread: 1.5" in with_spread


def test_awci_run_report_is_frozen():
    report = build_run_report()
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.valid_count = 999  # type: ignore[misc]
