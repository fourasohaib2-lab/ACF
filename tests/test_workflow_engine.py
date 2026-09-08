"""Unit test suite for ACF HPC Workflow Engine (ACF-HPC-104)."""

from pathlib import Path

import pytest

from acf.hpc_workflow.aladin.aladin_workflow import ALADINWorkflow
from acf.hpc_workflow.arome.arome_workflow import AROMEWorkflow
from acf.hpc_workflow.workflow_engine import (
    ExecutionSummary,
    ForecastCycle,
    StageResult,
    WorkflowConfig,
    WorkflowEngine,
    WorkflowStage,
)


def test_workflow_engine_arome():
    engine = WorkflowEngine()
    res = engine.run_arome_forecast(cycle="00UTC", forecast_length="24h")
    assert res["status"] == "SUCCESS"
    assert "job_id" in res


def test_workflow_engine_aladin():
    engine = WorkflowEngine()
    res = engine.run_aladin_forecast(cycle="12UTC", forecast_length="72h")
    assert res["status"] == "SUCCESS"
    assert "job_id" in res


def test_arome_and_aladin_workflow_instances():
    arome_wf = AROMEWorkflow()
    assert arome_wf.context.model_name == "AROME"

    aladin_wf = ALADINWorkflow()
    assert aladin_wf.context.model_name == "ALADIN"


def test_forecast_cycle_enum():
    assert ForecastCycle.from_string("00UTC") == ForecastCycle.UTC_00
    assert ForecastCycle.from_string("06") == ForecastCycle.UTC_06
    assert ForecastCycle.from_string("12 UTC") == ForecastCycle.UTC_12
    assert ForecastCycle.from_string("18") == ForecastCycle.UTC_18
    with pytest.raises(ValueError):
        ForecastCycle.from_string("22UTC")


def test_workflow_stage_enum():
    stages = [s.value for s in WorkflowStage]
    assert "INITIALIZATION" in stages
    assert "PREPROCESSING" in stages
    assert "OBSERVATION_CHECK" in stages
    assert "ASSIMILATION" in stages
    assert "SURFEX" in stages
    assert "PREP" in stages
    assert "MODEL_RUN" in stages
    assert "POST_PROCESSING" in stages
    assert "PRODUCT_GENERATION" in stages
    assert "QUALITY_CONTROL" in stages
    assert "ARCHIVING" in stages
    assert "CLEANUP" in stages


def test_workflow_engine_full_sequential_execution(tmp_path: Path):
    config = WorkflowConfig(
        work_dir=tmp_path / "work",
        output_dir=tmp_path / "output",
        archive_dir=tmp_path / "archive",
    )
    engine = WorkflowEngine(config=config)
    assert engine.initialize() is True

    summary = engine.execute(model_name="AROME", cycle=ForecastCycle.UTC_06, forecast_length="24h")
    assert isinstance(summary, ExecutionSummary)
    assert summary.status == "SUCCESS"
    assert len(summary.completed_stages) == 12
    assert summary.failed_stage is None


def test_workflow_engine_individual_stage_methods(tmp_path: Path):
    config = WorkflowConfig(
        work_dir=tmp_path / "work",
        output_dir=tmp_path / "output",
        archive_dir=tmp_path / "archive",
    )
    engine = WorkflowEngine(config=config)
    engine.initialize()

    context = engine.prepare_cycle(cycle="12UTC", model_name="ALADIN")

    res_assim = engine.run_assimilation(context)
    assert res_assim.success is True
    assert res_assim.stage == WorkflowStage.ASSIMILATION

    res_surfex = engine.run_surfex(context)
    assert res_surfex.success is True
    assert res_surfex.stage == WorkflowStage.SURFEX

    res_model = engine.run_model(context)
    assert res_model.success is True
    assert res_model.stage == WorkflowStage.MODEL_RUN

    res_post = engine.post_processing(context)
    assert res_post.success is True
    assert res_post.stage == WorkflowStage.POST_PROCESSING

    res_prod = engine.generate_products(context)
    assert res_prod.success is True
    assert res_prod.stage == WorkflowStage.PRODUCT_GENERATION

    res_arch = engine.archive_results(context)
    assert res_arch.success is True
    assert res_arch.stage == WorkflowStage.ARCHIVING

    res_clean = engine.cleanup(context)
    assert res_clean.success is True
    assert res_clean.stage == WorkflowStage.CLEANUP


def test_stage_metrics_are_honestly_flagged_as_simulated(tmp_path: Path):
    """
    CORRECTED: every stage's metrics dict (innovations_rms, min_pressure_hpa,
    cores_used, etc.) used to be presented with no disclosure that no real
    HPC backend (model binary, 3D-Var solver, SURFEX, observation network,
    job scheduler) is connected - just fixed illustrative numbers. Every
    stage now carries an explicit "simulated": True marker.
    """
    config = WorkflowConfig(
        work_dir=tmp_path / "work",
        output_dir=tmp_path / "output",
        archive_dir=tmp_path / "archive",
    )
    engine = WorkflowEngine(config=config)
    engine.initialize()
    context = engine.prepare_cycle(cycle="00UTC", model_name="AROME")

    for stage_call in (
        engine.run_preprocessing,
        engine.run_observation_check,
        engine.run_assimilation,
        engine.run_surfex,
        engine.run_prep,
        engine.run_model,
        engine.post_processing,
        engine.generate_products,
        engine.run_quality_control,
        engine.archive_results,
        engine.cleanup,
    ):
        result = stage_call(context)
        assert result.metrics.get("simulated") is True


def test_archive_results_reports_real_file_size_not_a_fixed_fake_value(tmp_path: Path):
    """CORRECTED: used to always report a fixed "size_bytes": 1024 regardless of the real archive file size."""
    config = WorkflowConfig(
        work_dir=tmp_path / "work",
        output_dir=tmp_path / "output",
        archive_dir=tmp_path / "archive",
    )
    engine = WorkflowEngine(config=config)
    engine.initialize()
    context = engine.prepare_cycle(cycle="00UTC", model_name="AROME")

    result = engine.archive_results(context)
    archive_path = Path(result.metrics["archive_path"])
    assert result.metrics["size_bytes"] == archive_path.stat().st_size
    assert result.metrics["size_bytes"] != 1024


def test_workflow_engine_stage_failure_halts_execution(tmp_path: Path, monkeypatch):
    config = WorkflowConfig(
        work_dir=tmp_path / "work",
        output_dir=tmp_path / "output",
        archive_dir=tmp_path / "archive",
    )
    engine = WorkflowEngine(config=config)
    engine.initialize()

    # Monkeypatch run_model to fail
    def failing_run_model(ctx):
        res = StageResult(
            stage=WorkflowStage.MODEL_RUN,
            success=False,
            start_time=0.0,
            end_time=1.0,
            duration_seconds=1.0,
            error_message="Simulated HPC node crash",
        )
        ctx.record_stage_result(res)
        return res

    monkeypatch.setattr(engine, "run_model", failing_run_model)

    summary = engine.execute(model_name="AROME", cycle="00UTC")
    assert summary.status == "FAILED"
    assert summary.failed_stage == WorkflowStage.MODEL_RUN
    assert WorkflowStage.POST_PROCESSING not in summary.completed_stages
