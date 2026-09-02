"""
ACF Job Engine
===============

Explicit user request: the "Prompt Maître ACF v2.0" master specification's
sections 22/46 describe a formal `Job` object (`job_id`/`status`/
`progress`/`retry_count`) - reports/ACF_MASTER_AUDIT_v2.md found this
genuinely absent: real HPC work already goes through
`acf.hpc_connector.job_manager.JobManager` (itself wrapping a real
`SlurmScheduler` doing genuine `sbatch`/`scancel`/`squeue` over SSH,
tested against the real Fennec cluster - see the audit's "HPC:
IMPLEMENTED, VALIDATED" finding) but with no generic, typed `Job`
abstraction above it.

What's built here
------------------
- `acf.jobs.job.Job`: the real, constructible §22/46 contract, plus
  `is_terminal()`/`is_failure()`/`is_success()` classification over
  ACF's own real, already-produced status strings (not an invented
  taxonomy) - see that module's own docstring for exactly which
  statuses count as what.
- `acf.jobs.job_engine.JobEngine`: real `submit`/`cancel`/`pause`/
  `resume`/`refresh_status`/`retry` operations, each delegating to
  `JobManager` (does not reimplement any scheduler call). `retry()` is
  new real behavior - genuinely resubmits a job that reached a real
  terminal failure status, carrying `retry_count` forward.

Fixed in passing (found while building this, not a separate session):
`acf.hpc_connector.scheduler_interface.SlurmScheduler.cancel_job()`
used to `return True` unconditionally regardless of the real SSH
result, and `get_job_status()` used to report "RUNNING" whenever
`squeue`'s real output was empty (which is squeue's normal output once
a job has already left the queue, not evidence it is still running).
Both now check the real, already-existing `RemoteExecutor`
"is_simulated"/`exit_code` markers - see that module's own "NOTE
(correction)" docstrings. `JobManager.pause_job()`/`resume_job()` used
to flip local status unconditionally with no real scheduler call at
all - now call genuine `scontrol suspend`/`resume` over SSH via two
new `SlurmScheduler` methods, using the exact same honest-confirmation
convention `cancel_job()` already established.
"""

from acf.jobs.job import Job, is_failure, is_success, is_terminal
from acf.jobs.job_engine import JobEngine

__all__ = ["Job", "JobEngine", "is_failure", "is_success", "is_terminal"]
