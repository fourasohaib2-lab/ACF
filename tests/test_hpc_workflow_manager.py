"""
Unit test suite for HPCWorkflowManager (ACF-HPC-004).

REWRITTEN: execute_workflow()/restart_workflow() used to assert a
fabricated "happy path" (status "COMPLETED") that traced back to the
FORECAST stage unconditionally marking itself "COMPLETED" right after
calling UniversalModelRunner.submit(), without checking whether the
job was actually submitted anywhere - which, with the default "local"
scheduler, it never was (see scheduler_interface.py/model_runner.py's
NOTE (correction) docstrings, fixed alongside this file). The workflow
now honestly fails at the FORECAST stage when no real scheduler
backend is wired up, instead of reporting a forecast as complete when
nothing ran.
"""

from acf.hpc_connector.workflow_manager import HPCWorkflowManager


def test_create_and_run_workflow():
    """Test creating and executing a full NWP workflow."""
    wm = HPCWorkflowManager()
    wf = wm.create_workflow("Daily_AROME", "AROME", {"nodes": 2})

    assert wf["status"] == "INITIALIZED"
    wf_id = wf["workflow_id"]

    # CORRECTED: with the default "local" scheduler, the FORECAST
    # stage's job is never actually submitted anywhere, so the
    # workflow now honestly reports FAILED instead of a fabricated
    # COMPLETED.
    res = wm.execute_workflow(wf_id)
    assert res["status"] == "FAILED"
    assert res["stages"]["PRE_PROCESSING"]["status"] == "COMPLETED"
    assert res["stages"]["FORECAST"]["status"] == "FAILED"

    status = wm.get_workflow_status(wf_id)
    assert status["progress_pct"] < 100.0


def test_workflow_restart():
    """Test restarting a workflow from a specific stage."""
    wm = HPCWorkflowManager()
    wf = wm.create_workflow("ARPEGE_Run", "ARPEGE", {})
    wf_id = wf["workflow_id"]

    res = wm.execute_workflow(wf_id)
    assert res["status"] == "FAILED"

    re_res = wm.restart_workflow(wf_id, from_stage="FORECAST")
    assert re_res["status"] == "FAILED"
    assert re_res["stages"]["FORECAST"]["status"] == "FAILED"
