"""
Tests for acf.jobs (the Prompt Maître ACF v2.0's §22/46 Job Engine),
plus the real-scheduler honesty fixes it required in
acf.hpc_connector.scheduler_interface/job_manager.
"""

from __future__ import annotations

import pytest

from acf.hpc_connector.job_manager import JobManager
from acf.hpc_connector.remote_executor import RemoteExecutor
from acf.hpc_connector.scheduler_interface import BaseSchedulerInterface, SlurmScheduler
from acf.hpc_connector.ssh_connector import SSHConnector
from acf.jobs.job import Job, is_failure, is_success, is_terminal
from acf.jobs.job_engine import JobEngine

# Same reserved-TLD convention as tests/test_hpc_connector.py - guaranteed to
# never resolve, so these tests never accidentally reach the real Fennec cluster.
OFFLINE_TEST_HOSTNAME = "test-offline-host.invalid"


class _FakeScheduler(BaseSchedulerInterface):
    """
    Deterministic double for JobEngine-level tests - real SSH/scheduler
    behavior is exercised separately below against the real
    SlurmScheduler (offline). Does not call super().__init__() (avoids
    constructing a real RemoteExecutor/PythonResolver this fake never
    uses).
    """

    def __init__(self) -> None:
        self.scheduler_name = "fake"
        self.cancel_result = True
        self.suspend_result = True
        self.resume_result = True
        self.status = "RUNNING"
        self.next_job_id_prefix = "FAKE_JOB"
        self._counter = 0

    def generate_batch_script(self, command, job_name="acf_sim", nodes=1, ntasks=1, gpus=0, walltime="01:00:00", partition="gpu"):
        return f"# fake script: {command}"

    def submit_job(self, job_script, job_name="acf_sim", nodes=1, ntasks=1) -> str:
        self._counter += 1
        return f"{self.next_job_id_prefix}_{self._counter}"

    def cancel_job(self, job_id: str) -> bool:
        return self.cancel_result

    def suspend_job(self, job_id: str) -> bool:
        return self.suspend_result

    def resume_job(self, job_id: str) -> bool:
        return self.resume_result

    def get_job_status(self, job_id: str) -> str:
        return self.status


def _engine() -> tuple[JobEngine, _FakeScheduler]:
    fake = _FakeScheduler()
    return JobEngine(JobManager(scheduler=fake)), fake


# ------------------------------------------------------------------ Job classification


@pytest.mark.parametrize("status", ["COMPLETED"])
def test_is_success(status):
    assert is_success(status) is True
    assert is_failure(status) is False
    assert is_terminal(status) is True


@pytest.mark.parametrize("status", ["CANCELLED", "FAILED", "TIMEOUT", "CANCEL_NOT_CONFIRMED", "NOT_SUBMITTED_NO_QSUB_CALL_WIRED_ab12"])
def test_is_failure(status):
    assert is_failure(status) is True
    assert is_success(status) is False
    assert is_terminal(status) is True


@pytest.mark.parametrize("status", ["RUNNING", "PENDING", "PAUSED", "UNKNOWN_NO_REAL_SCHEDULER_CONNECTION"])
def test_still_in_flight_statuses_are_not_terminal(status):
    assert is_terminal(status) is False
    assert is_failure(status) is False
    assert is_success(status) is False


def test_job_from_record_maps_the_real_job_manager_shape():
    record = {
        "job_id": "12345",
        "job_name": "arome_run",
        "command": "python -m acf.forecast.engine",
        "nodes": 4,
        "ntasks": 32,
        "gpus": 1,
        "partition": "gpu",
        "status": "RUNNING",
        "submit_time": "2026-09-02 00:00:00",
        "progress_pct": 0,
        "is_real_submission": True,
    }
    job = Job.from_record(record)
    assert job.job_id == "12345"
    assert job.job_name == "arome_run"
    assert job.nodes == 4
    assert job.is_real_submission is True
    assert job.retry_count == 0
    assert job.retried_from is None


# ------------------------------------------------------------------ JobEngine


def test_submit_returns_a_real_job_from_the_real_job_manager_record():
    engine, fake = _engine()
    job = engine.submit("run.sh", job_name="test_job", nodes=2, ntasks=4, gpus=1, partition="debug", walltime="00:30:00")

    assert isinstance(job, Job)
    assert job.job_id == "FAKE_JOB_1"
    assert job.job_name == "test_job"
    assert job.status == "RUNNING"
    assert job.is_real_submission is True
    assert job.walltime == "00:30:00"
    assert job.retry_count == 0


def test_submit_with_a_scheduler_that_never_really_submits_is_honestly_flagged():
    fake = _FakeScheduler()
    fake.next_job_id_prefix = "NOT_SUBMITTED_TEST"
    engine = JobEngine(JobManager(scheduler=fake))

    job = engine.submit("run.sh")

    assert job.is_real_submission is False
    assert job.job_id.startswith("NOT_SUBMITTED_")
    assert job.is_failure() is True  # NOT_SUBMITTED_* counts as a real terminal failure


def test_cancel_reflects_the_real_scheduler_result():
    engine, fake = _engine()
    job = engine.submit("run.sh")

    fake.cancel_result = True
    job = engine.cancel(job)
    assert job.status == "CANCELLED"


def test_cancel_reports_not_confirmed_when_the_scheduler_says_so():
    engine, fake = _engine()
    job = engine.submit("run.sh")

    fake.cancel_result = False
    job = engine.cancel(job)
    assert job.status == "CANCEL_NOT_CONFIRMED"
    assert job.is_failure() is True


def test_pause_and_resume_reflect_the_real_scheduler_result():
    engine, fake = _engine()
    job = engine.submit("run.sh")

    fake.suspend_result = True
    job = engine.pause(job)
    assert job.status == "PAUSED"

    fake.resume_result = True
    job = engine.resume(job)
    assert job.status == "RUNNING"


def test_pause_reports_not_confirmed_when_the_scheduler_says_so():
    engine, fake = _engine()
    job = engine.submit("run.sh")

    fake.suspend_result = False
    job = engine.pause(job)
    assert job.status == "PAUSE_NOT_CONFIRMED"


def test_refresh_status_reruns_a_real_query_against_the_scheduler():
    engine, fake = _engine()
    job = engine.submit("run.sh")
    assert job.status == "RUNNING"

    fake.status = "COMPLETED"
    job = engine.refresh_status(job)
    assert job.status == "COMPLETED"


def test_refresh_status_does_nothing_for_a_job_that_was_never_really_submitted():
    fake = _FakeScheduler()
    fake.next_job_id_prefix = "NOT_SUBMITTED_TEST"
    engine = JobEngine(JobManager(scheduler=fake))
    job = engine.submit("run.sh")

    fake.status = "COMPLETED"  # would only matter for a real submission
    job = engine.refresh_status(job)
    assert job.status.startswith("NOT_SUBMITTED_")  # unchanged


def test_retry_refuses_a_job_still_in_flight():
    engine, _fake = _engine()
    job = engine.submit("run.sh")  # status RUNNING - not a terminal failure

    with pytest.raises(ValueError, match="not in a terminal failure status"):
        engine.retry(job)


def test_retry_refuses_a_job_that_already_succeeded():
    engine, fake = _engine()
    job = engine.submit("run.sh")
    fake.status = "COMPLETED"
    job = engine.refresh_status(job)

    with pytest.raises(ValueError):
        engine.retry(job)


def test_retry_genuinely_resubmits_a_failed_job_with_the_same_parameters():
    engine, fake = _engine()
    job = engine.submit("run.sh", job_name="failing_job", nodes=2, ntasks=8, gpus=1, partition="gpu", walltime="02:00:00")
    fake.status = "FAILED"
    job = engine.refresh_status(job)
    assert job.is_failure() is True

    retried = engine.retry(job)

    assert retried.job_id != job.job_id  # a real resubmission gets a new real scheduler id
    assert retried.job_name == "failing_job"
    assert retried.nodes == 2
    assert retried.ntasks == 8
    assert retried.gpus == 1
    assert retried.walltime == "02:00:00"
    assert retried.retry_count == 1
    assert retried.retried_from == job.job_id
    assert retried.status == "RUNNING"  # the fake scheduler's default for a fresh submission


def test_retry_count_accumulates_across_repeated_retries():
    engine, fake = _engine()
    job = engine.submit("run.sh")
    fake.status = "FAILED"
    job = engine.refresh_status(job)

    job2 = engine.retry(job)
    fake.status = "FAILED"
    job2 = engine.refresh_status(job2)
    job3 = engine.retry(job2)

    assert job2.retry_count == 1
    assert job3.retry_count == 2
    assert job3.retried_from == job2.job_id


def test_get_and_list_return_real_jobs_with_their_tracked_retry_count():
    engine, fake = _engine()
    job = engine.submit("run.sh")
    fake.status = "FAILED"
    job = engine.refresh_status(job)
    retried = engine.retry(job)

    fetched = engine.get(retried.job_id)
    assert fetched is not None
    assert fetched.retry_count == 1
    assert fetched.retried_from == job.job_id

    all_jobs = engine.list()
    assert {j.job_id for j in all_jobs} == {job.job_id, retried.job_id}


def test_get_returns_none_for_an_unknown_job_id():
    engine, _fake = _engine()
    assert engine.get("never-submitted") is None


# ------------------------------------------------------------------ real SlurmScheduler honesty (offline)


def _offline_slurm_scheduler() -> SlurmScheduler:
    return SlurmScheduler(RemoteExecutor(SSHConnector(hostname=OFFLINE_TEST_HOSTNAME, username="sfoura")))


def test_slurm_cancel_job_is_honestly_false_with_no_real_ssh_transport():
    assert _offline_slurm_scheduler().cancel_job("12345") is False


def test_slurm_suspend_and_resume_job_are_honestly_false_with_no_real_ssh_transport():
    scheduler = _offline_slurm_scheduler()
    assert scheduler.suspend_job("12345") is False
    assert scheduler.resume_job("12345") is False


def test_slurm_get_job_status_is_honestly_unknown_with_no_real_ssh_transport():
    assert _offline_slurm_scheduler().get_job_status("12345") == "UNKNOWN_NO_REAL_SCHEDULER_CONNECTION"


def test_job_manager_pause_and_resume_propagate_the_real_offline_scheduler_result():
    """End-to-end proof at the JobManager layer: an offline (simulated) scheduler must make pause_job/resume_job honestly report unconfirmed, not silently succeed."""
    manager = JobManager(scheduler=_offline_slurm_scheduler())
    record = manager.submit_job("echo hi")  # NOT_SUBMITTED_* - offline, no real sbatch

    assert manager.pause_job(record["job_id"]) is False
    assert manager.active_jobs[record["job_id"]]["status"] == "PAUSE_NOT_CONFIRMED"

    assert manager.resume_job(record["job_id"]) is False
    assert manager.active_jobs[record["job_id"]]["status"] == "RESUME_NOT_CONFIRMED"
