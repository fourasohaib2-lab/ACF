"""HPC Queue Manager and Priority Tracker (ACF-HPC-001)."""

from typing import Any

from acf.hpc_connector.logging import log_hpc_event


class QueueManager:
    """Manages job queues, priority scheduling, and dependencies."""

    def __init__(self) -> None:
        self.queues: dict[str, list[dict[str, Any]]] = {
            "gpu": [],
            "compute": [],
            "highmem": [],
            "debug": [],
        }

    def enqueue_job(self, job_info: dict[str, Any], queue_name: str = "gpu") -> bool:
        """Add job info to target queue."""
        q = queue_name.lower()
        if q not in self.queues:
            self.queues[q] = []
        self.queues[q].append(job_info)
        log_hpc_event("INFO", f"Enqueued job {job_info.get('job_id')} in queue [{q}]")
        return True

    def get_queue_status(self) -> dict[str, int]:
        """Return summary of job counts per queue."""
        return {k: len(v) for k, v in self.queues.items()}
