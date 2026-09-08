"""
Tests for acf.awci.pipeline - the real orchestrated §8/§31 pipeline
(explicit priority freely chosen from the 90-section exhaustive audit's
own remaining ⚠️ gaps: "each step exists somewhere but never assembled
into one real, named, orchestrated, traceable sequence").
run_awci_point_pipeline() is a real ASSEMBLER over already-real,
already-tested functions - these tests verify it wires them together
correctly, not that it reimplements any of their science.
"""

from __future__ import annotations

from acf.awci.calculator import AWCICalculator
from acf.awci.pipeline import PipelineStage, quality_for_awci_point_data, run_awci_point_pipeline

_DATA = {"temperature": 300.0, "wind_speed": 25.0, "specific_humidity": 0.015, "pressure": 850.0, "cape": 1800.0}


# --------------------------------------------------- quality_for_awci_point_data


def test_quality_matches_a_direct_input_adapter_style_assessment():
    quality = quality_for_awci_point_data(_DATA)
    assert set(quality.keys()) == {"air_temperature", "specific_humidity", "wind_speed", "air_pressure"}
    for status in quality.values():
        assert status.status == "VALID"


def test_quality_honestly_reports_a_genuinely_missing_variable():
    partial = {"temperature": 300.0, "wind_speed": 25.0}  # no specific_humidity/pressure
    quality = quality_for_awci_point_data(partial)
    assert quality["specific_humidity"].status == "MISSING"
    assert quality["air_pressure"].status == "MISSING"
    assert quality["air_temperature"].status == "VALID"


def test_quality_uses_the_real_pressure_unit_conversion_not_a_second_one():
    """Real regression guard: must reuse acf.awci.input_adapter's own
    hPa-vs-Pa fix, not silently re-diverge from it."""
    low_pressure = {**_DATA, "pressure": 5.0}  # 500 Pa - below the real OPERATIONAL_RANGES floor
    quality = quality_for_awci_point_data(low_pressure)
    assert quality["air_pressure"].status == "OUT_OF_RANGE"


# --------------------------------------------------- run_awci_point_pipeline


def test_pipeline_result_matches_a_direct_calculate_with_uncertainty_call():
    pipeline_result = run_awci_point_pipeline(dict(_DATA))
    expected = AWCICalculator().calculate_with_uncertainty(dict(_DATA))

    assert pipeline_result.result.awci == expected["awci"]
    assert pipeline_result.result.level == expected["level"]
    assert pipeline_result.result.module_scores == expected["module_scores"]


def test_pipeline_result_carries_real_quality():
    pipeline_result = run_awci_point_pipeline(dict(_DATA))
    assert pipeline_result.result.quality is not None
    assert pipeline_result.result.quality["air_temperature"].status == "VALID"


def test_pipeline_result_carries_the_real_raw_variables_and_context():
    pipeline_result = run_awci_point_pipeline(dict(_DATA), vertical_level=3, lead_time_hours=6.0)
    assert pipeline_result.result.raw_variables == _DATA
    assert pipeline_result.result.vertical_level == 3
    assert pipeline_result.result.lead_time_hours == 6.0


def test_pipeline_execution_report_matches_a_direct_summarize_execution_call():
    from acf.awci.execution_report import summarize_execution

    pipeline_result = run_awci_point_pipeline(dict(_DATA))
    direct = summarize_execution(pipeline_result.result)
    assert pipeline_result.execution_report.render() == direct.render()


def test_pipeline_stages_are_real_pipeline_stage_objects_in_order():
    pipeline_result = run_awci_point_pipeline(dict(_DATA))
    names = [s.name for s in pipeline_result.stages]
    assert names[:5] == [
        "variable_mapping_and_quality_control",
        "module_interaction_uncertainty_calculation",
        "consensus_engine",
        "products",
        "validation_and_observability",
    ]
    for stage in pipeline_result.stages:
        assert isinstance(stage, PipelineStage)
        assert stage.status in {"RAN", "SKIPPED", "NOT_APPLICABLE"}
        assert stage.detail  # never an empty/placeholder string


def test_consensus_engine_stage_is_skipped_without_real_model_spread():
    pipeline_result = run_awci_point_pipeline(dict(_DATA))
    consensus = next(s for s in pipeline_result.stages if s.name == "consensus_engine")
    assert consensus.status == "SKIPPED"


def test_consensus_engine_stage_shows_ran_when_the_caller_supplies_real_model_spread():
    model_spread = {"disagreement_spread": 1.5, "field": "T"}
    pipeline_result = run_awci_point_pipeline(dict(_DATA), model_spread=model_spread, model_spread_level="LOW")
    consensus = next(s for s in pipeline_result.stages if s.name == "consensus_engine")
    assert consensus.status == "RAN"
    assert pipeline_result.result.model_spread == model_spread
    assert pipeline_result.execution_report.model_spread_level == "LOW"


def test_not_applicable_stages_are_honestly_disclosed_never_silently_dropped():
    pipeline_result = run_awci_point_pipeline(dict(_DATA))
    na_names = {s.name for s in pipeline_result.stages if s.status == "NOT_APPLICABLE"}
    assert na_names == {"discovery", "ingestion", "format_detection", "visualization", "dashboard"}


def test_pipeline_is_deterministic_for_the_same_real_input():
    a = run_awci_point_pipeline(dict(_DATA))
    b = run_awci_point_pipeline(dict(_DATA))
    assert a.result.awci == b.result.awci
    assert a.result.module_scores == b.result.module_scores


def test_uncertainty_stage_reflects_a_real_ensemble_when_supplied():
    data_with_ensemble = {
        **_DATA,
        "ensemble_members": {"wind_speed": [20.0, 25.0, 30.0], "cape": [1500.0, 1800.0, 2100.0]},
    }
    pipeline_result = run_awci_point_pipeline(data_with_ensemble)
    uncertainty_stage = pipeline_result.stages[1]
    assert uncertainty_stage.name == "module_interaction_uncertainty_calculation"
    assert "n_realizations=3" in uncertainty_stage.detail
