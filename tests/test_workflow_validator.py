"""Unit test suite for hpc_workflow/workflow_validator.py and workflow.py (ACF-HPC-104)."""

import pytest

from acf.hpc_workflow.workflow import BaseWorkflow
from acf.hpc_workflow.workflow_context import WorkflowContext
from acf.hpc_workflow.workflow_errors import WorkflowValidationError
from acf.hpc_workflow.workflow_validator import WorkflowValidator


def test_validate_stage_accepts_a_valid_cycle():
    validator = WorkflowValidator()
    context = WorkflowContext(workflow_id="wf1", model_name="AROME", cycle="00UTC")
    assert validator.validate_stage("MODEL_RUN", context) is True


def test_validate_stage_rejects_an_invalid_cycle():
    validator = WorkflowValidator()
    context = WorkflowContext(workflow_id="wf1", model_name="AROME", cycle="99UTC")
    with pytest.raises(WorkflowValidationError, match="Invalid forecast cycle"):
        validator.validate_stage("MODEL_RUN", context)


def test_validate_stage_check_is_identical_regardless_of_stage_name():
    """
    CORRECTED (docs): despite the "20 workflow stages" framing,
    validate_stage() performs exactly one check (cycle format)
    identically for any stage name - documented as such rather than
    implying real per-stage validation rules that don't exist.
    """
    validator = WorkflowValidator()
    context = WorkflowContext(workflow_id="wf1", model_name="AROME", cycle="00UTC")
    for stage in ("INITIALIZATION", "ASSIMILATION", "ARCHIVING", "some_unknown_stage"):
        assert validator.validate_stage(stage, context) is True


def test_base_workflow_run_stage_updates_progress():
    wf = BaseWorkflow(workflow_id="wf1", model_name="AROME", cycle="12UTC")
    assert wf.run_stage("PREPROCESSING") is True
    assert wf.context.progress.current_stage == "PREPROCESSING"


def test_base_workflow_run_stage_propagates_invalid_cycle():
    wf = BaseWorkflow(workflow_id="wf1", model_name="AROME", cycle="99UTC")
    with pytest.raises(WorkflowValidationError):
        wf.run_stage("MODEL_RUN")
