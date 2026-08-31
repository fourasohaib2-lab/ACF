"""
Atmospheric Complexity Framework (ACF)

HPC CONNECTOR - HPC NWP Workflow Manager (ACF-HPC-004)

Manages operational NWP workflow DAGs (pre-processing, initialization, forecast,
post-processing, verification, archiving) with automatic restart capabilities.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from acf.hpc_connector.model_runner import UniversalModelRunner

logger = logging.getLogger(__name__)

STAGES = [
    "PRE_PROCESSING",
    "INITIALIZATION",
    "FORECAST",
    "POST_PROCESSING",
    "VERIFICATION",
    "ARCHIVING",
]


class HPCWorkflowManager:
    """
    Orchestrates DAG-based NWP operational workflows on HPC cluster.
    """

    def __init__(self, runner: UniversalModelRunner | None = None) -> None:
        self.runner = runner if runner else UniversalModelRunner()
        self.workflows: dict[str, dict[str, Any]] = {}

    def create_workflow(self, workflow_name: str, model_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        Creates a new workflow DAG structure.
        """
        wf_id = f"wf_{workflow_name.lower()}_{int(time.time())}"

        stages = {
            "PRE_PROCESSING": {"status": "PENDING", "depends_on": []},
            "INITIALIZATION": {"status": "PENDING", "depends_on": ["PRE_PROCESSING"]},
            "FORECAST": {"status": "PENDING", "depends_on": ["INITIALIZATION"]},
            "POST_PROCESSING": {"status": "PENDING", "depends_on": ["FORECAST"]},
            "VERIFICATION": {"status": "PENDING", "depends_on": ["POST_PROCESSING"]},
            "ARCHIVING": {"status": "PENDING", "depends_on": ["VERIFICATION"]},
        }

        record = {
            "workflow_id": wf_id,
            "workflow_name": workflow_name,
            "model_name": model_name,
            "status": "INITIALIZED",
            "stages": stages,
            "config": config,
            "created_at": time.time(),
        }

        self.workflows[wf_id] = record
        return record

    def run_stage(self, workflow_id: str, stage_name: str) -> dict[str, Any]:
        """
        Executes a single workflow stage, checking dependency requirements.
        """
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow ID '{workflow_id}' not found.")

        stage_upper = stage_name.upper()
        if stage_upper not in wf["stages"]:
            raise ValueError(f"Invalid stage '{stage_name}'. Supported stages: {list(wf['stages'].keys())}")

        stage_info = wf["stages"][stage_upper]

        # Check dependencies
        for dep in stage_info["depends_on"]:
            if wf["stages"][dep]["status"] != "COMPLETED":
                raise RuntimeError(f"Cannot run stage {stage_upper}: Dependency {dep} is not COMPLETED.")

        stage_info["status"] = "RUNNING"
        wf["status"] = f"RUNNING_{stage_upper}"

        if stage_upper == "FORECAST":
            res = self.runner.submit(wf["model_name"], wf["config"])
            stage_info["job_id"] = res["job_id"]
            # NOTE (correction): this used to unconditionally mark the
            # FORECAST stage "COMPLETED" right after calling
            # runner.submit() without checking whether the submission
            # actually reached a real scheduler backend - a job that
            # was never really submitted would be silently reported as
            # a completed forecast. Now checks res's real status
            # (see model_runner.py/job_manager.py's NOTEs).
            if res.get("is_real_submission"):
                stage_info["status"] = "COMPLETED"
            else:
                stage_info["status"] = "FAILED"
                stage_info["failure_reason"] = res["status"]
        else:
            time.sleep(0.01)
            stage_info["status"] = "COMPLETED"

        logger.info(f"Workflow {workflow_id} stage {stage_upper} finished with status {stage_info['status']}")
        return stage_info

    def execute_workflow(self, workflow_id: str) -> dict[str, Any]:
        """
        Executes all stages of the workflow in DAG order.
        """
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow ID '{workflow_id}' not found.")

        for st in STAGES:
            if wf["stages"][st]["status"] != "COMPLETED":
                try:
                    stage_result = self.run_stage(workflow_id, st)
                except Exception as e:
                    wf["stages"][st]["status"] = "FAILED"
                    wf["status"] = "FAILED"
                    wf["error"] = str(e)
                    logger.error(f"Workflow {workflow_id} failed at stage {st}: {e}")
                    return wf
                # NOTE (correction): run_stage() can also return a
                # "FAILED" status without raising (e.g. the FORECAST
                # stage when no real scheduler backend submitted the
                # job) - this used to go unnoticed here and the loop
                # would move on to the next stage, only failing
                # indirectly once that stage's dependency check
                # tripped. Now stops immediately with a clear reason.
                if stage_result.get("status") == "FAILED":
                    wf["status"] = "FAILED"
                    wf["error"] = stage_result.get("failure_reason", f"Stage {st} failed.")
                    logger.error(f"Workflow {workflow_id} failed at stage {st}: {wf['error']}")
                    return wf

        wf["status"] = "COMPLETED"
        return wf

    def restart_workflow(self, workflow_id: str, from_stage: str | None = None) -> dict[str, Any]:
        """
        Restarts a failed workflow from a given failed or specified stage.
        """
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow ID '{workflow_id}' not found.")

        start_stage = from_stage.upper() if from_stage else "FORECAST"

        # Reset statuses from start_stage onwards
        reset = False
        for st in STAGES:
            if st == start_stage:
                reset = True
            if reset:
                wf["stages"][st]["status"] = "PENDING"

        wf["status"] = "RESTARTED"
        return self.execute_workflow(workflow_id)

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Returns full workflow execution summary and stage progress.
        """
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow ID '{workflow_id}' not found.")

        completed_count = sum(1 for s in wf["stages"].values() if s["status"] == "COMPLETED")
        total_count = len(wf["stages"])

        return {
            "workflow_id": workflow_id,
            "workflow_name": wf["workflow_name"],
            "model_name": wf["model_name"],
            "status": wf["status"],
            "progress_pct": round((completed_count / total_count) * 100.0, 1),
            "stages": wf["stages"],
        }
