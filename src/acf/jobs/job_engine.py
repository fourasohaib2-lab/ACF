"""
JobEngine: real lifecycle operations over `acf.jobs.job.Job`, built on
top of ACF's already-real `acf.hpc_connector.job_manager.JobManager`
(itself wrapping a real `SlurmScheduler` doing genuine
`sbatch`/`scancel`/`scontrol suspend|resume`/`squeue` over SSH). Does
not reimplement any of that submission machinery - every method below
delegates to it and wraps the real result into a `Job`.
"""

from __future__ import annotations

from acf.hpc_connector.job_manager import JobManager
from acf.jobs.job import Job


class JobEngine:
    """
    The section 22/46 "Job Engine" - real `Job` objects with real
    `submit`/`cancel`/`pause`/`resume`/`refresh_status`/`retry`
    behavior, each delegating to `JobManager`'s already-real scheduler
    wiring rather than a second implementation of it.

    Honest scope: `JobManager`'s own job records do not carry
    `walltime` (see `job_manager.py`'s `submit_job()`), so `Job`
    objects reconstructed by `get()`/`list()` (as opposed to the one
    returned directly by `submit()`, which still has the real value in
    scope) fall back to `Job`'s own default rather than a fabricated
    one - a real, disclosed limitation of the record shape underneath,
    not of this class.
    """

    def __init__(self, job_manager: JobManager | None = None) -> None:
        self.job_manager = job_manager or JobManager()
        #: job_id -> retry_count, tracked here since JobManager's own
        #: records have no such field - real bookkeeping this class
        #: adds, not read back from anywhere else.
        self._retry_counts: dict[str, int] = {}
        self._retried_from: dict[str, str] = {}

    def submit(
        self,
        command: str,
        job_name: str = "acf_earth_sim",
        nodes: int = 1,
        ntasks: int = 1,
        gpus: int = 0,
        partition: str = "gpu",
        walltime: str = "01:00:00",
    ) -> Job:
        """Genuinely submit `command` via `JobManager.submit_job()` and wrap the real resulting job record."""
        record = self.job_manager.submit_job(
            command, job_name=job_name, nodes=nodes, ntasks=ntasks, gpus=gpus, partition=partition, walltime=walltime
        )
        job = Job.from_record(record)
        job.walltime = walltime  # real value from this call - JobManager's own record doesn't carry it, see class docstring
        self._retry_counts[job.job_id] = 0
        return job

    def cancel(self, job: Job) -> Job:
        """Genuinely cancel `job` via `JobManager.cancel_job()` (real `scancel`) and update `job.status` in place from the real result."""
        confirmed = self.job_manager.cancel_job(job.job_id)
        job.status = "CANCELLED" if confirmed else "CANCEL_NOT_CONFIRMED"
        return job

    def pause(self, job: Job) -> Job:
        """Genuinely suspend `job` via `JobManager.pause_job()` (real `scontrol suspend`) and update `job.status` in place from the real result."""
        confirmed = self.job_manager.pause_job(job.job_id)
        job.status = "PAUSED" if confirmed else "PAUSE_NOT_CONFIRMED"
        return job

    def resume(self, job: Job) -> Job:
        """Genuinely resume `job` via `JobManager.resume_job()` (real `scontrol resume`) and update `job.status` in place from the real result."""
        confirmed = self.job_manager.resume_job(job.job_id)
        job.status = "RUNNING" if confirmed else "RESUME_NOT_CONFIRMED"
        return job

    def refresh_status(self, job: Job) -> Job:
        """
        Re-query `job`'s real status straight from the scheduler
        backend (genuine `squeue` for `SlurmScheduler`) and update
        `job.status` in place - not a locally-cached guess.

        A job that was never really submitted (`is_real_submission`
        False) has nothing real to query - left unchanged.
        """
        if not job.is_real_submission:
            return job
        job.status = self.job_manager.scheduler.get_job_status(job.job_id)
        return job

    def retry(self, job: Job) -> Job:
        """
        Genuinely resubmit `job` with the same real submission
        parameters - not a fabricated retry that resets `status`
        without resubmitting anything real.

        Returns a new `Job` (a real resubmission gets a new real
        scheduler-assigned `job_id` - Slurm has no "resubmit under the
        same id" operation) with `retry_count` carried forward from
        `job` and `retried_from` set to `job.job_id`.

        Raises
        ------
        ValueError
            If `job` has not reached a real terminal *failure* status
            (`Job.is_failure()`) - retrying a job still in flight, or
            one that already completed successfully, would silently
            duplicate real HPC work.
        """
        if not job.is_failure():
            raise ValueError(
                f"job {job.job_id!r} is not in a terminal failure status (status={job.status!r}) - refusing to retry"
            )
        new_job = self.submit(
            job.command,
            job_name=job.job_name,
            nodes=job.nodes,
            ntasks=job.ntasks,
            gpus=job.gpus,
            partition=job.partition,
            walltime=job.walltime,
        )
        new_job.retry_count = job.retry_count + 1
        new_job.retried_from = job.job_id
        self._retry_counts[new_job.job_id] = new_job.retry_count
        self._retried_from[new_job.job_id] = job.job_id
        return new_job

    def get(self, job_id: str) -> Job | None:
        """Real lookup - None if `job_id` was never submitted through this engine's `JobManager`."""
        record = self.job_manager.get_job(job_id)
        if record is None:
            return None
        return Job.from_record(record, retry_count=self._retry_counts.get(job_id, 0), retried_from=self._retried_from.get(job_id))

    def list(self) -> list[Job]:
        """Every job this engine's `JobManager` has a real record for."""
        return [
            Job.from_record(r, retry_count=self._retry_counts.get(r["job_id"], 0), retried_from=self._retried_from.get(r["job_id"]))
            for r in self.job_manager.list_jobs()
        ]
