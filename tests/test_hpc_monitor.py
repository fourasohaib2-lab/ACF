"""
Unit test suite for ACF HPC Monitor (ACF-HPC-003).

REWRITTEN (disconnected-state tests added): every method used to fall back
to hard-coded, realistic-looking fake cluster/job data (e.g. jobs
"acf_arome_00z"/"acf_aladin_00z" RUNNING/PENDING, "142 jobs submitted, 138
completed, 2 failed") with zero disclosure whenever squeue/sacct/sinfo/
scontrol/sdiag were unavailable - which is the case in essentially any
environment outside a real, configured Slurm cluster. The existing
mocked-real-output tests above were never affected (none of them exercised
the fake-fallback path), but no test previously locked in what happens when
nothing is connected at all - added below.
"""

from acf.hpc_connector import HPCMonitor
from acf.hpc_connector.hpc_monitor import HPCMonitor as HPCMonitorClass


class MockRemoteExecutor:
    """Mock executor returning custom Slurm output strings."""

    def __init__(self, responses: dict):
        self.responses = responses

    def execute_command(self, cmd: str) -> str:
        for prefix, resp in self.responses.items():
            if cmd.startswith(prefix):
                return resp
        return ""


def test_hpc_monitor_creation():
    """Test creating HPCMonitor instance."""
    monitor = HPCMonitor(cluster_name="Fennec")
    assert monitor is not None
    assert isinstance(monitor, HPCMonitorClass)
    assert monitor.cluster_name == "Fennec"


def test_list_jobs_mocked():
    """Test list_jobs output parsing with mock squeue output."""
    mock_squeue = (
        "2001|arome_run_00z|sfoura|RUNNING|01:23:45|4|node[01-04]\n"
        "2002|aladin_run_00z|sfoura|PENDING|00:00:00|2|node05\n"
    )
    executor = MockRemoteExecutor({"squeue": mock_squeue})
    monitor = HPCMonitor(remote_executor=executor)

    jobs = monitor.list_jobs(user="sfoura")
    assert len(jobs) == 2
    assert jobs[0]["job_id"] == "2001"
    assert jobs[0]["job_name"] == "arome_run_00z"
    assert jobs[0]["state"] == "RUNNING"
    assert jobs[0]["nodes"] == 4
    assert jobs[1]["job_id"] == "2002"
    assert jobs[1]["state"] == "PENDING"


def test_get_job_history_mocked():
    """Test get_job_history output parsing with mock sacct output."""
    mock_sacct = "2001|COMPLETED|02:15:30|4|node[01-04]|0:0\n"
    executor = MockRemoteExecutor({"sacct": mock_sacct})
    monitor = HPCMonitor(remote_executor=executor)

    history = monitor.get_job_history("2001")
    assert history["job_id"] == "2001"
    assert history["state"] == "COMPLETED"
    assert history["elapsed_time"] == "02:15:30"
    assert history["nodes"] == 4
    assert history["exit_code"] == "0:0"


def test_cluster_status_and_health_mocked():
    """Test cluster_status and get_cluster_health methods."""
    mock_sinfo = "Researches*|up|20/12/0/32\n"
    executor = MockRemoteExecutor({"sinfo": mock_sinfo})
    monitor = HPCMonitor(remote_executor=executor, cluster_name="Fennec")

    status = monitor.cluster_status()
    assert status["idle_nodes"] == 12
    assert status["allocated_nodes"] == 20
    assert status["down_nodes"] == 0

    health = monitor.get_cluster_health()
    assert health["cluster"] == "Fennec"
    assert health["scheduler"] == "slurm"
    assert health["nodes_total"] == 32
    assert health["nodes_idle"] == 12


def test_node_health_cpu_memory_mocked():
    """Test get_node_health, get_cpu_usage, and get_memory_usage."""
    mock_scontrol = (
        "NodeName=node01 CPUTot=64 CPUAlloc=32 RealMemory=256000 State=ALLOCATED\n\n"
        "NodeName=node02 CPUTot=64 CPUAlloc=0 RealMemory=256000 State=IDLE\n"
    )
    executor = MockRemoteExecutor({"scontrol": mock_scontrol})
    monitor = HPCMonitor(remote_executor=executor)

    health_list = monitor.get_node_health()
    assert len(health_list) == 2
    assert health_list[0]["healthy"] is True

    cpu_usage = monitor.get_cpu_usage()
    assert cpu_usage["cpus_total"] == 128
    assert cpu_usage["cpus_allocated"] == 32

    mem_usage = monitor.get_memory_usage()
    assert mem_usage["memory_total_mb"] == 512000


def test_slurm_statistics():
    """Test get_slurm_statistics."""
    mock_sdiag = "server_thread_count: 8\njobs_submitted: 200\n"
    executor = MockRemoteExecutor({"sdiag": mock_sdiag})
    monitor = HPCMonitor(remote_executor=executor)

    stats = monitor.get_slurm_statistics()
    assert stats["server_thread_count"] == "8"
    assert stats["jobs_submitted"] == "200"


def test_error_resilience():
    """Test error handling when remote executor raises exceptions or binary is missing."""

    class FailingExecutor:
        def execute_command(self, cmd: str):
            raise TimeoutError("Execution timed out")

    monitor = HPCMonitor(remote_executor=FailingExecutor())

    jobs = monitor.list_jobs()
    assert isinstance(jobs, list)

    health = monitor.get_cluster_health()
    assert health["scheduler"] == "slurm"
    assert "nodes_total" in health


class _AlwaysEmptyExecutor:
    """Executor that always returns empty output, simulating no real Slurm binaries available."""

    def execute_command(self, cmd: str) -> str:
        return ""


def test_list_jobs_honestly_empty_when_disconnected():
    """CORRECTED: used to fabricate 2 fake jobs (1001/1002, acf_arome_00z/acf_aladin_00z)."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    assert monitor.list_jobs() == []


def test_get_job_history_honestly_not_connected():
    """CORRECTED: used to fabricate a fake 'COMPLETED' history for ANY job_id."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    history = monitor.get_job_history("9999")
    assert history["connected"] is False
    assert history["state"] == "NOT_AVAILABLE_NO_SCHEDULER_BACKEND_CONNECTED"
    assert history["elapsed_time"] is None


def test_cluster_status_honestly_zero_when_disconnected():
    """CORRECTED: used to fabricate a fake 32-node cluster (12 idle, 20 allocated, 2 partitions)."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    status = monitor.cluster_status()
    assert status == {"idle_nodes": 0, "allocated_nodes": 0, "down_nodes": 0, "partitions": [], "connected": False}


def test_node_status_honestly_empty_or_not_connected():
    """CORRECTED: used to fabricate 2 fake nodes (node01 ALLOCATED, node02 IDLE)."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    assert monitor.node_status() == []

    single = monitor.node_status("nodeXX")
    assert single["connected"] is False
    assert single["state"] == "NOT_AVAILABLE_NO_SCHEDULER_BACKEND_CONNECTED"
    assert single["cpus_total"] is None


def test_get_slurm_statistics_honestly_not_connected():
    """CORRECTED: used to fabricate '142 jobs submitted, 138 completed, 2 failed' for any disconnected cluster."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    stats = monitor.get_slurm_statistics()
    assert stats["connected"] is False
    assert stats["jobs_submitted"] is None


def test_get_cluster_health_honestly_zero_when_disconnected():
    """
    CORRECTED: `nodes_total` used to fall back to a fabricated 32 whenever
    idle+alloc+down summed to 0 - including the genuinely disconnected
    case - silently claiming a 32-node cluster exists with nothing queried.
    """
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    health = monitor.get_cluster_health()
    assert health["connected"] is False
    assert health["nodes_total"] == 0
    assert health["cpu_load"] is None
    assert health["memory_available"] is None


def test_get_cpu_usage_honestly_none_when_disconnected():
    """CORRECTED: `cpu_load_pct` used to fall back to a fabricated 50.0% with no real nodes queried."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    cpu = monitor.get_cpu_usage()
    assert cpu["connected"] is False
    assert cpu["cpu_load_pct"] is None
    assert cpu["cpus_total"] == 0


def test_get_memory_usage_honestly_none_when_disconnected():
    """CORRECTED: `memory_available_pct` used to fall back to a fabricated 75.0% with no real nodes queried."""
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    mem = monitor.get_memory_usage()
    assert mem["connected"] is False
    assert mem["memory_available_pct"] is None


def test_get_node_health_and_partition_status_honestly_empty_when_disconnected():
    monitor = HPCMonitor(remote_executor=_AlwaysEmptyExecutor())
    assert monitor.get_node_health() == []
    assert monitor.get_partition_status() == []


def test_real_data_paths_still_carry_a_connected_true_marker():
    """Real, successfully-parsed data must be positively marked connected, not just 'not obviously fake'."""
    mock_squeue = "2001|arome_run_00z|sfoura|RUNNING|01:23:45|4|node[01-04]\n"
    executor = MockRemoteExecutor({"squeue": mock_squeue})
    monitor = HPCMonitor(remote_executor=executor)

    jobs = monitor.list_jobs()
    assert jobs[0]["connected"] is True
