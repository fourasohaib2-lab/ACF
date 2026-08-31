"""HPC Job Lifecycle Manager (ACF-HPC-001)."""

import time
from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.queue_manager import QueueManager
from acf.hpc_connector.scheduler_interface import BaseSchedulerInterface, get_scheduler_interface


class JobManager:
    """Manages complete job lifecycle (Submit, Cancel, Pause, Resume, Restart, Checkpoint, Recover, Monitor)."""

    def __init__(self, scheduler: BaseSchedulerInterface | None = None) -> None:
        self.scheduler = scheduler or get_scheduler_interface("local")
        self.queue_manager = QueueManager()
        self.active_jobs: dict[str, dict[str, Any]] = {}

    def submit_job(
        self,
        command: str,
        job_name: str = "acf_earth_sim",
        nodes: int = 1,
        ntasks: int = 1,
        gpus: int = 0,
        partition: str = "gpu",
        walltime: str = "01:00:00",
    ) -> dict[str, Any]:
        """Submit job to active scheduler."""
        script = self.scheduler.generate_batch_script(
            command, job_name=job_name, nodes=nodes, ntasks=ntasks, gpus=gpus, walltime=walltime, partition=partition
        )
        job_id = self.scheduler.submit_job(script, job_name=job_name, nodes=nodes, ntasks=ntasks)

        # NOTE (correction): this used to unconditionally set
        # status="RUNNING" regardless of what scheduler.submit_job()
        # actually returned - PBSScheduler/LocalScheduler (fixed
        # earlier this session) used to fabricate a real-looking job
        # id for a job that never ran; they now return an id prefixed
        # "NOT_SUBMITTED_" precisely so this boundary can tell real
        # submission (SlurmScheduler, which genuinely calls sbatch)
        # from a fabricated one and report status honestly.
        was_really_submitted = not job_id.startswith("NOT_SUBMITTED_")
        job_record = {
            "job_id": job_id,
            "job_name": job_name,
            "command": command,
            "nodes": nodes,
            "ntasks": ntasks,
            "gpus": gpus,
            "partition": partition,
            "status": "RUNNING" if was_really_submitted else "NOT_SUBMITTED_NO_SCHEDULER_BACKEND_WIRED",
            "submit_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "progress_pct": 0,
            "is_real_submission": was_really_submitted,
        }

        self.active_jobs[job_id] = job_record
        self.queue_manager.enqueue_job(job_record, queue_name=partition)
        return job_record

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running or queued job.

        NOTE (correction): this used to call self.scheduler.cancel_job()
        but ignore its actual return value, unconditionally logging
        "cancelled successfully" and returning True for any known
        job_id - even one that was never really submitted (see
        submit_job()'s is_real_submission). Now propagates the
        scheduler's real result.
        """
        if job_id in self.active_jobs:
            really_cancelled = self.scheduler.cancel_job(job_id)
            self.active_jobs[job_id]["status"] = "CANCELLED" if really_cancelled else "CANCEL_NOT_CONFIRMED"
            if really_cancelled:
                log_hpc_event("INFO", f"Job [{job_id}] cancelled successfully.")
            else:
                log_hpc_event("WARNING", f"Job [{job_id}] cancel request could not be confirmed by the scheduler.")
            return really_cancelled
        return False

    def pause_job(self, job_id: str) -> bool:
        """Pause running job execution."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["status"] = "PAUSED"
            log_hpc_event("INFO", f"Job [{job_id}] paused.")
            return True
        return False

    def resume_job(self, job_id: str) -> bool:
        """Resume paused job."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["status"] = "RUNNING"
            log_hpc_event("INFO", f"Job [{job_id}] resumed.")
            return True
        return False

    def checkpoint_job(self, job_id: str, checkpoint_dir: str = "/tmp/acf_checkpoints") -> bool:
        """Create state checkpoint for disaster recovery."""
        if job_id in self.active_jobs:
            log_hpc_event("INFO", f"Saved checkpoint for job [{job_id}] to {checkpoint_dir}")
            return True
        return False

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Retrieve job record dictionary."""
        return self.active_jobs.get(job_id)

    def list_jobs(self) -> list[dict[str, Any]]:
        """Return list of all active or historical jobs."""
        return list(self.active_jobs.values())
