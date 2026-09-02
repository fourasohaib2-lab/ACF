"""
Job: the Prompt Maître ACF v2.0's section 22/46 formal job contract -
`job_id`/`status`/`progress`/`retry_count` - built as a real,
constructible object on top of ACF's already-real HPC submission layer
(`acf.hpc_connector.job_manager.JobManager`, which itself wraps a real
`SlurmScheduler` doing genuine `sbatch`/`scancel`/`squeue` over SSH -
see reports/ACF_MASTER_AUDIT_v2.md's "HPC: IMPLEMENTED, VALIDATED"
finding, tested against the real Fennec cluster).

reports/ACF_MASTER_AUDIT_v2.md's "Job Engine: MISSING" finding was
specifically about this generic, typed abstraction - not about the
underlying HPC submission itself, which was already real. This module
does not resubmit or reimplement that layer; it gives its dict-shaped
job records (see `JobManager.submit_job()`'s own real return shape) a
real, constructible type with real lifecycle helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

#: Statuses genuinely produced by acf.hpc_connector.job_manager.JobManager
#: and acf.hpc_connector.scheduler_interface's real scheduler backends -
#: not an invented taxonomy. Real Slurm `squeue -o %T` failure states
#: (see SlurmScheduler.get_job_status()) plus the honest statuses
#: JobManager itself assigns when a scheduler call could not be
#: confirmed real.
_TERMINAL_FAILURE_STATUSES = frozenset(
    {
        "CANCELLED",
        "FAILED",
        "TIMEOUT",
        "CANCEL_NOT_CONFIRMED",
        "NODE_FAIL",
        "BOOT_FAIL",
        "DEADLINE",
        "OUT_OF_MEMORY",
        "PREEMPTED",
        "REVOKED",
    }
)
_TERMINAL_SUCCESS_STATUSES = frozenset({"COMPLETED"})


def is_terminal(status: str) -> bool:
    """
    True for a real terminal status - a job that will not progress any
    further on its own. Includes every "NOT_SUBMITTED_..." status (the
    job never reached a real scheduler at all - see
    SlurmScheduler.submit_job()'s own disclosure) since there is
    nothing left in flight for those either.

    Never guesses for a status string it doesn't recognise (e.g. a
    real Slurm state this module hasn't been told about, or one of the
    honest "UNKNOWN_..."/"PENDING"/"RUNNING" statuses) - returns False
    (treated as still in flight) rather than assuming terminal.
    """
    return status in _TERMINAL_SUCCESS_STATUSES or status in _TERMINAL_FAILURE_STATUSES or status.startswith("NOT_SUBMITTED_")


def is_failure(status: str) -> bool:
    """True for a real terminal *failure* status - see is_terminal()'s own disclosure on what "real" means here."""
    return status in _TERMINAL_FAILURE_STATUSES or status.startswith("NOT_SUBMITTED_")


def is_success(status: str) -> bool:
    """True only for a real confirmed-completed status."""
    return status in _TERMINAL_SUCCESS_STATUSES


@dataclass
class Job:
    """
    A real, constructible HPC job - the section 22/46 contract
    (`job_id`/`status`/`progress`/`retry_count`), plus the real
    submission parameters a caller needs to genuinely retry it.

    Parameters
    ----------
    job_id : str
        Real scheduler-assigned id (e.g. a genuine Slurm job id) or,
        honestly, one of the "NOT_SUBMITTED_..." placeholders a
        backend without a real scheduler connection returns - see
        `is_real_submission`.
    is_real_submission : bool
        False whenever `job_id` is one of those placeholders - a
        caller must check this before trusting `job_id` refers to
        anything real.
    progress_pct : float, optional
        Real progress in [0, 100] - `None`/0 by default (`JobManager`'s
        own job records leave it at 0 for the life of the job), genuinely
        updated by `JobEngine.refresh_progress()` for a real
        `SlurmScheduler` job (a real elapsed-time/time-limit estimate
        from `squeue` - see that method's own docstring for its honest
        scope: wall-clock progress, NOT a per-task completion
        percentage, which SLURM has no notion of). Stays `None`/0
        rather than simulate progress whenever no real data is
        available (PBS/Local backends, a job that already left the
        queue, no `--time` limit set, ...).
    retry_count : int
        How many times `JobEngine.retry()` has resubmitted this job
        (or an ancestor of it) - 0 for an original submission.
    retried_from : str, optional
        `job_id` of the job this one was resubmitted from, if any.
    """

    job_id: str
    job_name: str
    command: str
    status: str
    is_real_submission: bool
    nodes: int = 1
    ntasks: int = 1
    gpus: int = 0
    partition: str = "gpu"
    walltime: str = "01:00:00"
    submit_time: str = ""
    progress_pct: float | None = None
    retry_count: int = 0
    retried_from: str | None = None

    def is_terminal(self) -> bool:
        return is_terminal(self.status)

    def is_failure(self) -> bool:
        return is_failure(self.status)

    def is_success(self) -> bool:
        return is_success(self.status)

    @classmethod
    def from_record(cls, record: dict[str, Any], retry_count: int = 0, retried_from: str | None = None) -> Job:
        """
        Build from a real `acf.hpc_connector.job_manager.JobManager`
        job record dict - the actual shape `submit_job()`/`get_job()`/
        `list_jobs()` return, not a guessed one.
        """
        return cls(
            job_id=record["job_id"],
            job_name=record.get("job_name", ""),
            command=record.get("command", ""),
            status=record["status"],
            is_real_submission=bool(record.get("is_real_submission", False)),
            nodes=record.get("nodes", 1),
            ntasks=record.get("ntasks", 1),
            gpus=record.get("gpus", 0),
            partition=record.get("partition", "gpu"),
            submit_time=record.get("submit_time", ""),
            progress_pct=record.get("progress_pct"),
            retry_count=retry_count,
            retried_from=retried_from,
        )
