"""
Unit test suite for UniversalModelRunner (ACF-HPC-004).

REWRITTEN: submit()/cancel()/restart() used to assert a fabricated
"happy path" (status "SUBMITTED", cancel() returning True) that
actually traced back to LocalScheduler/PBSScheduler (in
scheduler_interface.py) returning a plausible-looking fake job id and
unconditionally claiming success, with no real job ever submitted,
cancelled, or tracked (RemoteExecutor is SSH-only by design, so the
default "local" scheduler has no real local-execution backend wired
up - see scheduler_interface.py's NOTE (correction) docstrings). The
file-based parts of the pipeline (prepare_case, collect_outputs,
archive) are genuinely real and are still exercised and asserted as
before; the scheduler-dependent parts now assert the honest
NOT_SUBMITTED outcome instead of a fabricated success.
"""

from pathlib import Path

import pytest

from acf.hpc_connector.model_runner import SUPPORTED_MODELS, UniversalModelRunner


def test_prepare_case_supported_models():
    """Test preparing test cases for all supported models."""
    runner = UniversalModelRunner()
    for model in SUPPORTED_MODELS:
        case = runner.prepare_case(model, {"walltime": "01:00:00"})
        assert case["model_name"] == model
        assert case["status"] == "PREPARED"
        assert Path(case["work_dir"]).exists()


def test_prepare_case_unsupported_model():
    """Test error handling when requesting an unsupported model."""
    runner = UniversalModelRunner()
    with pytest.raises(ValueError):
        runner.prepare_case("UNSUPPORTED_NWP_MODEL", {})


def test_submit_and_monitor():
    """Test submitting (honestly, with no real scheduler backend) and monitoring NWP jobs."""
    runner = UniversalModelRunner()
    res = runner.submit("AROME", {"nodes": 2, "cpus_per_node": 16})

    # CORRECTED: with the default "local" scheduler, no real job is
    # actually submitted anywhere (LocalScheduler has no execution
    # backend wired up) - status now honestly reflects that instead of
    # a fabricated "SUBMITTED".
    assert res["status"] == "NOT_SUBMITTED_NO_SCHEDULER_BACKEND_WIRED"
    assert res["is_real_submission"] is False
    assert "job_id" in res

    job_id = res["job_id"]
    mon = runner.monitor(job_id)
    assert mon["job_id"] == job_id


def test_cancel_restart_archive(tmp_path: Path):
    """Test cancelling, restarting, collecting outputs, and archiving jobs."""
    runner = UniversalModelRunner()
    res = runner.submit("ALADIN", {"nodes": 1})
    job_id = res["job_id"]

    # CORRECTED: cancel() used to unconditionally claim True - with no
    # real scheduler backend, there is nothing to genuinely cancel.
    assert runner.cancel(job_id) is False

    re_res = runner.restart(job_id, checkpoint_step=12)
    assert re_res["status"] == "NOT_SUBMITTED_NO_SCHEDULER_BACKEND_WIRED"

    # collect_outputs()/archive() are genuine file operations
    # (independent of whether any real job ran) - unaffected.
    outputs = runner.collect_outputs(job_id, str(tmp_path / "outs"))
    assert len(outputs) >= 1

    arch = runner.archive(job_id, str(tmp_path / "arch"))
    assert Path(arch).exists()
