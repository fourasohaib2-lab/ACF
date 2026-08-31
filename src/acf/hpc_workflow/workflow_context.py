"""HPC Workflow Execution Context & Progress Metrics (ACF-HPC-104)."""

import time
from dataclasses import dataclass, field
from typing import Any

from acf.hpc_workflow.workflow_status import WorkflowStatus


@dataclass
class WorkflowProgress:
    """Tracks progress percentage, completed tasks, and ETA."""

    forecast_pct: float = 0.0
    completed_tasks: int = 0
    total_tasks: int = 10
    current_stage: str = "INITIALIZATION"
    estimated_completion_seconds: float = 300.0


@dataclass
class WorkflowContext:
    """Operational workflow execution context dataclass."""

    workflow_id: str
    model_name: str
    cycle: str = "00UTC"
    forecast_length: str = "24h"
    status: WorkflowStatus = WorkflowStatus.INITIALIZING
    job_id: str = ""
    progress: WorkflowProgress = field(default_factory=WorkflowProgress)
    created_at: float = field(default_factory=time.time)
    attributes: dict[str, Any] = field(default_factory=dict)
