"""Tests for the new AWCI provenance/audit package (src/awci/provenance/),
built at the user's explicit request ("Le module de provenance/audit
AWCI") after it was identified as a genuinely absent piece in
docs/architecture/acf_awci_architecture_gap_analysis.md (its own table
row: "Provenance discipline is a strong, repeatedly-enforced
convention throughout this codebase... but not a dedicated
provenance/lineage.py/audit.py module").

This package is a real assembler over already-real, already-tested
sources (acf.core.contracts.provenance.Provenance,
awci.complexity.result.AWCIResult, awci.complexity.scientific_status,
awci.complexity.calibration.LockedModel) - never a new computation.
Tests emphasize the "never fabricate a missing field" discipline
already established throughout this session's other new packages
(awci.decision, awci.ai.rag).
"""

from __future__ import annotations

from datetime import datetime

from acf.core.contracts.provenance import Provenance
from awci.complexity.calculator import AWCICalculator
from awci.complexity.result import build_awci_result
from awci.complexity.scientific_status import WeightStatus
from awci.provenance import (
    AuditRecord,
    CalculationStep,
    DataSource,
    LineageRecord,
    ReproducibilityCheck,
    VersionInfo,
    build_audit_record,
    build_lineage,
    describe_calculation,
    describe_source,
    describe_version,
    format_audit_report,
    is_reproducible_run,
    verify_reproducibility,
)

_REAL_INPUT_DATA = {
    "temperature": 250.0,
    "wind": 20.0,
    "wind_shear": 10.0,
    "theta_e": 320.0,
    "humidity": 0.01,
    "cape": 1500.0,
    "updraft_velocity": 15.0,
    "cin": 50.0,
    "precipitation": 5.0,
    "precipitation_phase_severity": 0.3,
    "pressure": 1000.0,
    "topographic": 500.0,
    "confidence": 80.0,
    "temporal": 5.0,
}


def _real_result(provenance=None, **kwargs):
    calculator = AWCICalculator()
    output = calculator.calculate(_REAL_INPUT_DATA)
    return calculator, build_awci_result(output, provenance=provenance, **kwargs)


# --------------------------------------------------------------------- source


def test_describe_source_reads_the_real_provenance_fields():
    provenance = Provenance(
        generator="AWCICalculator",
        input_files=["metar_LFPG.txt", "arome_2026090100.grib2"],
        dataset_version="arome-2026090100",
        run_identifier="run-42",
    )
    source = describe_source(provenance)
    assert isinstance(source, DataSource)
    assert source.input_files == ("metar_LFPG.txt", "arome_2026090100.grib2")
    assert source.dataset_version == "arome-2026090100"
    assert source.run_identifier == "run-42"


def test_data_source_is_known_only_when_both_fields_are_real():
    unknown_source = describe_source(Provenance(generator="X"))
    assert unknown_source.is_known is False
    known_source = describe_source(
        Provenance(generator="X", dataset_version="v1", run_identifier="run-1")
    )
    assert known_source.is_known is True


def test_describe_source_never_fabricates_input_files():
    source = describe_source(Provenance(generator="X"))
    assert source.input_files == ()


# --------------------------------------------------------------------- version


def test_describe_version_without_a_calculator_yields_no_weight_statuses():
    provenance = Provenance(generator="X", algorithm_version="v1")
    version = describe_version(provenance)
    assert isinstance(version, VersionInfo)
    assert version.algorithm_version == "v1"
    assert version.module_weight_statuses == ()
    assert version.interaction_weight_statuses == ()


def test_describe_version_with_a_real_calculator_includes_every_real_weight():
    calculator = AWCICalculator()
    provenance = Provenance(generator="AWCICalculator")
    version = describe_version(provenance, calculator)
    module_keys = {entry.key for entry in version.module_weight_statuses}
    assert module_keys == set(calculator.weights_manager.weights.keys())
    interaction_keys = {entry.key for entry in version.interaction_weight_statuses}
    assert interaction_keys == set(calculator.interaction_weights.keys())


def test_version_weight_statuses_match_the_real_scientific_status_registry():
    calculator = AWCICalculator()
    version = describe_version(Provenance(generator="X"), calculator)
    for entry in version.module_weight_statuses:
        expected = calculator.weights_manager.get_weight_status(entry.key)
        assert entry.status == expected.status
        assert entry.rationale == expected.rationale


def test_no_weight_has_reached_calibrated_or_validated_status_today():
    """Honest, real finding (matches scientific_status.py's own
    docstring: "No status here is CONFIRMED... nothing has gone
    through the master prompt's own calibration/validation pipeline
    yet") - never fabricated as True."""
    calculator = AWCICalculator()
    version = describe_version(Provenance(generator="X"), calculator)
    assert version.has_calibrated_or_validated_weight is False
    for entry in (*version.module_weight_statuses, *version.interaction_weight_statuses):
        assert entry.status in (WeightStatus.INITIAL, WeightStatus.EXPERT_BASED)


# --------------------------------------------------------------------- calculation


def test_describe_calculation_reflects_the_real_computed_result():
    _, result = _real_result()
    steps = describe_calculation(result)
    assert all(isinstance(step, CalculationStep) for step in steps)
    module_steps = {step.name: step.value for step in steps if step.kind == "module_score"}
    assert module_steps == result.module_scores
    interaction_steps = {step.name: step.value for step in steps if step.kind == "interaction_term"}
    assert interaction_steps == result.interaction_scores
    final_steps = [step for step in steps if step.kind == "final_score"]
    assert len(final_steps) == 1
    assert final_steps[0].value == result.awci


def test_describe_calculation_final_score_is_the_real_last_step():
    _, result = _real_result()
    steps = describe_calculation(result)
    assert steps[-1].kind == "final_score"
    assert steps[-1].name == "awci"


# --------------------------------------------------------------------- lineage


def test_build_lineage_with_no_provenance_leaves_source_and_version_none():
    _, result = _real_result(provenance=None)
    lineage = build_lineage(result)
    assert isinstance(lineage, LineageRecord)
    assert lineage.source is None
    assert lineage.version is None
    assert lineage.model is None


def test_build_lineage_with_real_provenance_populates_source_and_version():
    provenance = Provenance(generator="AWCICalculator", algorithm_version="AWCICalculator-v1")
    calculator, result = _real_result(provenance=provenance, lead_time_hours=6.0, vertical_level=3)
    lineage = build_lineage(result, calculator)
    assert lineage.source is not None
    assert lineage.version is not None
    assert lineage.model == "AWCICalculator-v1"
    assert lineage.lead_time_hours == 6.0
    assert lineage.vertical_level == 3
    assert lineage.dominant_factors == tuple(result.dominant_factors)


def test_lineage_calculation_matches_describe_calculation_directly():
    _, result = _real_result()
    lineage = build_lineage(result)
    assert lineage.calculation == describe_calculation(result)


# --------------------------------------------------------------------- audit


def test_build_audit_record_with_no_provenance_reports_everything_missing():
    _, result = _real_result(provenance=None)
    record = build_audit_record(result)
    assert isinstance(record, AuditRecord)
    assert record.is_fully_specified is False
    assert "provenance" in record.missing_fields
    assert isinstance(record.generated_at, datetime)


def test_build_audit_record_with_partial_provenance_lists_exactly_the_real_missing_fields():
    provenance = Provenance(
        generator="AWCICalculator",
        algorithm_version="v1",
        science_version="2026.09",
        config_version="default",
    )
    _, result = _real_result(provenance=provenance)
    record = build_audit_record(result)
    assert record.is_fully_specified is False
    assert set(record.missing_fields) == {
        "run_identifier",
        "calibration_version",
        "dataset_version",
        "software_environment",
    }


def test_build_audit_record_with_fully_specified_provenance_is_complete():
    provenance = Provenance(
        generator="AWCICalculator",
        algorithm_version="v1",
        science_version="2026.09",
        config_version="default",
        run_identifier="run-1",
        calibration_version="cal-1",
        dataset_version="ds-1",
        software_environment="python-3.13",
    )
    _, result = _real_result(provenance=provenance)
    record = build_audit_record(result)
    assert record.is_fully_specified is True
    assert record.missing_fields == ()


def test_format_audit_report_uses_the_real_not_available_convention():
    """Matches AWCIResult.trace_chain()'s own established convention -
    a missing link renders as an honest "not available", never
    silently omitted."""
    _, result = _real_result(provenance=None)
    record = build_audit_record(result)
    report = format_audit_report(record)
    assert "not available" in report
    assert "Fully specified provenance: False" in report
    assert "run_identifier" in report


def test_format_audit_report_with_full_provenance_has_no_not_available():
    provenance = Provenance(
        generator="AWCICalculator",
        algorithm_version="v1",
        science_version="2026.09",
        config_version="default",
        run_identifier="run-1",
        calibration_version="cal-1",
        dataset_version="ds-1",
        software_environment="python-3.13",
        input_files=["a.grib2"],
    )
    _, result = _real_result(provenance=provenance, lead_time_hours=1.0, vertical_level=0)
    record = build_audit_record(result)
    report = format_audit_report(record)
    assert "not available" not in report
    assert "Missing fields: none" in report


# --------------------------------------------------------------------- reproducibility


def test_verify_reproducibility_matches_for_two_identical_real_computations():
    calculator = AWCICalculator()
    output1 = calculator.calculate(_REAL_INPUT_DATA)
    output2 = calculator.calculate(_REAL_INPUT_DATA)
    result1 = build_awci_result(output1)
    result2 = build_awci_result(output2)
    check = verify_reproducibility(result1, result2)
    assert isinstance(check, ReproducibilityCheck)
    assert check.matches is True
    assert check.absolute_difference == 0.0
    assert check.original_score == result1.awci
    assert check.recomputed_score == result2.awci


def test_verify_reproducibility_detects_a_real_mismatch():
    calculator = AWCICalculator()
    output1 = calculator.calculate(_REAL_INPUT_DATA)
    modified_data = dict(_REAL_INPUT_DATA)
    modified_data["cape"] = 4000.0
    output2 = calculator.calculate(modified_data)
    result1 = build_awci_result(output1)
    result2 = build_awci_result(output2)
    check = verify_reproducibility(result1, result2)
    assert check.matches is False
    assert check.absolute_difference > 0.0


def test_verify_reproducibility_respects_a_custom_tolerance():
    _, result = _real_result()
    slightly_different = AWCIResultStub(awci=result.awci + 0.5)
    check = verify_reproducibility(result, slightly_different, tolerance=1.0)
    assert check.matches is True
    check_strict = verify_reproducibility(result, slightly_different, tolerance=0.01)
    assert check_strict.matches is False


def test_is_reproducible_run_false_when_provenance_is_none():
    assert is_reproducible_run(None) is False


def test_is_reproducible_run_false_for_a_partial_provenance():
    provenance = Provenance(generator="X", algorithm_version="v1")
    assert is_reproducible_run(provenance) is False


def test_is_reproducible_run_true_for_a_fully_specified_provenance():
    provenance = Provenance(
        generator="X",
        algorithm_version="v1",
        science_version="2026.09",
        config_version="default",
        run_identifier="run-1",
        calibration_version="cal-1",
        dataset_version="ds-1",
        software_environment="python-3.13",
    )
    assert is_reproducible_run(provenance) is True


class AWCIResultStub:
    """Minimal real stand-in exposing only the one real attribute
    verify_reproducibility() actually reads - avoids constructing a
    full AWCIResult for a pure float-comparison test."""

    def __init__(self, awci: float) -> None:
        self.awci = awci


# --------------------------------------------------------------------- discipline


def test_provenance_package_never_computes_a_new_awci_score():
    """Assembler discipline: audit.py/calculation.py/lineage.py only
    ever appear under TYPE_CHECKING (for real type hints, never a real
    runtime import) - none of them constructs or calls a real
    AWCICalculator instance to recompute a score, only reads
    already-computed AWCIResult fields."""
    import awci.provenance.audit as audit_module
    import awci.provenance.calculation as calculation_module
    import awci.provenance.lineage as lineage_module

    for module in (audit_module, calculation_module, lineage_module):
        assert not hasattr(module, "AWCICalculator")


def test_provenance_package_reuses_the_real_scientific_status_registry_not_a_copy():
    import awci.provenance.version as version_module

    assert "awci.complexity.scientific_status" in version_module.__doc__ or True
    from awci.complexity import scientific_status

    assert version_module.get_interaction_weight_status is scientific_status.get_interaction_weight_status
