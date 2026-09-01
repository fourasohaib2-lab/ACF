"""Unit test suite for ACF-HPC-101 Universal PythonResolver & SLURM Compute Node Environment Bootstrapper."""

from acf.gui.esoc.module_registry import ModuleRegistry
from acf.hpc_connector.arome_aladin_detector import AromeAladinDetector
from acf.hpc_connector.cluster_detector import ClusterDetector
from acf.hpc_connector.configuration import HPCConfiguration
from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.hpc_connector.environment_manager import EnvironmentManager
from acf.hpc_connector.python_resolver import PythonResolver
from acf.hpc_connector.remote_executor import RemoteExecutor
from acf.hpc_connector.scheduler_interface import (
    SlurmScheduler,
)
from acf.hpc_connector.file_transfer import FileTransferManager
from acf.hpc_connector.remote_terminal import RemoteTerminalShell
from acf.hpc_connector.security import HPCSecurityManager
from acf.hpc_connector.ssh_connector import SSHConnector


def test_python_resolver_discovery():
    executor = RemoteExecutor()
    resolver = PythonResolver(executor)

    modules = resolver.discover_python_modules()
    assert len(modules) > 0
    assert any("Python" in m or "python" in m for m in modules)

    executables = resolver.discover_python_executables()
    assert "python3" in executables or "python3.11" in executables


def test_python_resolver_versions():
    resolver = PythonResolver()

    # Version tuple parsing tests
    assert resolver._parse_version_tuple("3.11.5") == (3, 11, 5)
    assert resolver._parse_version_tuple("3.10.12") == (3, 10, 12)
    assert resolver._parse_version_tuple("3.9.1") == (3, 9, 1)
    assert resolver._parse_version_tuple("3.8.0") == (3, 8, 0)
    assert resolver._parse_version_tuple("3.6.8") == (3, 6, 8)

    # Resolution test
    info = resolver.resolve_python()
    assert info["is_valid"] is True
    assert "python_path" in info
    assert "python_version" in info


def test_slurm_scheduler_dynamic_python():
    slurm = SlurmScheduler()
    script = slurm.generate_batch_script("python -m acf.forecast.engine", job_name="arome_dynamic_python")

    assert "#SBATCH --job-name=arome_dynamic_python" in script
    assert "export PYTHON_EXECUTABLE=" in script
    assert "/usr/bin/python3.11" not in script  # Ensure no hardcoded binary path!


def test_hpc_configuration():
    config = HPCConfiguration("config/hpc.yaml")
    mode = config.get_execution_mode()
    assert mode in ["local", "cluster", "hybrid", "gpu", "mpi", "distributed"]
    profile = config.get_cluster_profile("university_hpc")
    assert "scheduler" in profile
    assert profile["scheduler"] == "slurm"


def test_cluster_and_arome_detector():
    executor = RemoteExecutor()
    detector = ClusterDetector(executor)
    info = detector.detect_all()
    assert "os" in info
    assert "cpu" in info
    assert "gpu" in info
    assert "interconnect" in info

    # CORRECTED: every detect_*() method used to unconditionally claim
    # fixed, plausible-looking hardware/software (always "slurm", always
    # "has_mpi": True, always "InfiniBand HDR 200 Gbps", etc.) regardless
    # of whether self.executor genuinely reached a real remote system -
    # several methods (scheduler/containers/environment/interconnect)
    # didn't even call execute_command() at all. In this offline/dev
    # test environment (no real FENNEC SSH transport), every claim must
    # now honestly disclose it as not real rather than fabricate a
    # specific answer.
    assert info["scheduler"]["is_real_data"] is False
    assert info["scheduler"]["type"] == "unknown"
    assert info["mpi"]["is_real_data"] is False
    assert info["mpi"]["has_mpi"] is False
    assert info["containers"]["is_real_data"] is False
    assert info["environment"]["is_real_data"] is False
    assert info["interconnect"]["is_real_data"] is False
    assert info["interconnect"]["bandwidth_gbps"] is None

    # get_scheduler_interface() must gracefully fall back to LocalScheduler
    # for the honest "unknown" scheduler type rather than assuming Slurm.
    hpc = HPCConnectionManager("config/hpc.yaml")
    assert hpc.scheduler.scheduler_name != "slurm"

    arome_detector = AromeAladinDetector(executor)
    stack = arome_detector.detect_meteorological_stack()
    assert "operational_mode" in stack
    assert "has_arome" in stack
    assert "has_aladin" in stack


def test_security_manager():
    sec = HPCSecurityManager()
    assert isinstance(sec.has_valid_ssh_key(), bool)
    assert sec.validate_connection("login2.fennec.meteo.dz", "sfoura") is True


def test_environment_manager():
    env = EnvironmentManager()
    res = env.setup_environment(["gcc/12.2.0", "eccodes/2.30.0", "openmpi/4.1.5"])
    assert "loaded_modules" in res
    assert "gcc/12.2.0" in res["loaded_modules"]


def test_paramiko_ssh_and_executor():
    ssh = SSHConnector(hostname="login2.fennec.meteo.dz", username="sfoura")
    assert ssh.connect() is True
    assert ssh.is_alive() is True
    executor = RemoteExecutor(ssh)
    res = executor.execute_command("echo 'FENNEC HPC OPERATIONAL'")
    assert res["exit_code"] == 0
    assert "execution_time" in res
    assert ssh.disconnect() is True


def test_file_transfer_manager_honest_status_when_no_real_sftp(tmp_path):
    """
    CORRECTED: SSHConnector.upload()/download() and
    FileTransferManager.sync_files()/download_results() used to
    unconditionally return True / record "status": "COMPLETED" even when
    no SFTP channel could be opened - the default outcome in this offline
    development environment (no real FENNEC connectivity). Now honestly
    reports failure instead of a fabricated success.
    """
    ssh = SSHConnector(hostname="login2.fennec.meteo.dz", username="sfoura")
    assert ssh.connect() is True
    assert ssh.is_alive() is True  # offline dev mode: honestly "alive" per this class's own convention

    source = tmp_path / "checkpoint.nc"
    source.write_bytes(b"fake netcdf payload for checksum testing")

    manager = FileTransferManager(connector=ssh)

    # No real SFTP transport is available in this environment, so the
    # upload cannot actually happen - this must be reported honestly.
    uploaded = manager.sync_files(str(source), "/scratch/users/sfoura/checkpoint.nc")
    assert uploaded is False
    assert manager.transfer_history[-1]["status"] == "FAILED_NO_REAL_TRANSFER"
    # A real file did exist and was readable, so its checksum must be a
    # genuine 64-hex-char SHA256 digest, not a fabricated placeholder.
    assert len(manager.transfer_history[-1]["checksum"]) == 64

    downloaded = manager.download_results("/scratch/users/sfoura/result.nc", str(tmp_path / "result.nc"))
    assert downloaded is False

    # A missing source file must report an explicit "no checksum" sentinel,
    # never a value indistinguishable from - or colliding with - another
    # missing file's placeholder.
    missing_checksum = manager.compute_sha256(str(tmp_path / "does_not_exist.nc"))
    assert missing_checksum == "NO_CHECKSUM_FILE_NOT_FOUND"


def test_remote_terminal_shell_open_shell_honest_when_no_real_channel():
    """
    CORRECTED: RemoteTerminalShell.open_shell() used to unconditionally
    return True even when invoke_shell() raised (the default outcome in
    this offline environment, same root cause as the SFTP fix above:
    is_alive() is honestly True with no real transport, so invoke_shell()
    is attempted on an unconnected client and raises) or when no live
    connector/client was available at all. self.channel stays None in
    both cases - the return value must reflect that, not claim success.
    """
    ssh = SSHConnector(hostname="login2.fennec.meteo.dz", username="sfoura")
    assert ssh.connect() is True
    assert ssh.is_alive() is True

    terminal = RemoteTerminalShell(connector=ssh)
    opened = terminal.open_shell()
    assert opened is False
    assert terminal.channel is None

    # send_command() must still work via its documented fallback (direct
    # SSH execution) even though no persistent channel was opened.
    output = terminal.send_command("echo hello")
    assert isinstance(output, str)


def test_hpc_connection_manager_fennec_workflow():
    hpc = HPCConnectionManager("config/hpc.yaml")
    assert hpc.connect("university_hpc") is True
    assert hpc.is_connected is True
    assert "python_path" in hpc.cluster_info
    assert "python_version" in hpc.cluster_info

    # One-Click AROME pipeline test
    # CORRECTED: "status" used to be unconditionally "SUCCESS" regardless
    # of whether self.scheduler.submit_job() actually reached a real
    # SLURM scheduler - it now honestly reflects the NOT_SUBMITTED_
    # contract shared with JobManager, and no real scheduler is
    # connected in this test environment.
    arome_res = hpc.execute_one_click_arome()
    assert arome_res["is_real_submission"] is False
    assert arome_res["status"] != "SUCCESS"
    assert "job_id" in arome_res

    # CORRECTED: benchmark_performance() used to claim "PASSED" with 8
    # fixed fabricated benchmark numbers, with no real stress test ever
    # run against the cluster.
    bench = hpc.benchmark_performance()
    assert bench["status"] == "NOT_BENCHMARKED_NO_LIVE_PROBE_CONNECTED"
    assert bench["cpu_gflops"] is None

    summary = hpc.get_status_summary()
    assert summary["connected"] is True
    # CORRECTED: telemetry used to be a fixed fabricated snapshot
    # (mpi_active_ranks == 128 always) with no real probe run.
    assert summary["telemetry"]["status"] == "NOT_MEASURED_NO_LIVE_TELEMETRY_PROBE_CONNECTED"
    assert summary["telemetry"]["mpi_active_ranks"] is None
    assert hpc.disconnect() is True


def test_esoc_module_registry_integration():
    registry = ModuleRegistry()
    assert registry.is_connected("hpc_connector") is True
    hpc_mod = registry.get_module("hpc_connector")
    assert hpc_mod is not None
