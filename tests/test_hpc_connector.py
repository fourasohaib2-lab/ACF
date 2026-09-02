"""Unit test suite for ACF-HPC-101 Universal PythonResolver & SLURM Compute Node Environment Bootstrapper."""

import sys

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

# CORRECTED: this whole file used to construct SSHConnector/HPCConnectionManager
# against the real "login2.fennec.meteo.dz" default hostname, on the (previously
# true) assumption that no real network path could ever reach it, so every
# "offline dev mode" assertion here was safe regardless of what machine ran the
# suite. A separate fix (ssh_connector.py's DNS-gating bug) made real connection
# attempts genuinely happen for any resolvable hostname - and on a machine that IS
# on the ONM network (this one), login2.fennec.meteo.dz resolves to a real
# 10.16.20.2 and these tests began actually reaching the real Fennec cluster over
# SSH. Unit tests must never depend on - or accidentally exercise - real
# production network access. ".invalid" is an IANA/RFC 2606-reserved TLD
# guaranteed to never resolve in any real DNS, so tests using it stay
# deterministic and network-safe on every machine, not just ones without a route
# to Fennec.
OFFLINE_TEST_HOSTNAME = "test-offline-host.invalid"


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

    # CORRECTED: there used to be no way to tell whether python_path/
    # python_version were genuinely confirmed against a live remote probe
    # or fell back to this process's own local sys.executable (still
    # accurate, but not the same claim). In this offline test environment
    # (no real FENNEC SSH transport), it must honestly report the local
    # fallback was used, not a fabricated remote verification.
    assert info["is_remote_verified"] is False
    assert info["python_path"] == sys.executable


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

    # CORRECTED: "university_hpc" doesn't exist in config/hpc.yaml's
    # cluster_profiles (only "fennec" does) - get_cluster_profile()
    # used to silently substitute an arbitrary different real cluster's
    # profile instead of honestly reporting "not found".
    profile = config.get_cluster_profile("fennec")
    assert "scheduler" in profile
    assert profile["scheduler"] == "slurm"

    missing = config.get_cluster_profile("university_hpc")
    assert missing == {}


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

    # CORRECTED: every `which <binary>` shell command used to embed its
    # OWN guaranteed-success fallback (`|| echo 'AROME_FOUND'`) so a
    # genuinely-missing binary could never actually be reported as
    # missing, has_canari/has_odb/has_eccodes were hardcoded True with
    # zero detection attempted, and models_detected was a fixed 5-item
    # list regardless of what was actually "detected". In this offline
    # test environment (no real FENNEC SSH transport), none of these
    # binaries can genuinely be confirmed present.
    assert stack["has_arome"] is False
    assert stack["has_aladin"] is False
    assert stack["has_canari"] is False
    assert stack["has_odb"] is False
    assert stack["has_eccodes"] is False
    assert stack["eccodes_version"] is None
    assert stack["models_detected"] == []
    assert stack["operational_mode"] == "STANDARD_NWP"


def test_security_manager():
    sec = HPCSecurityManager()
    assert isinstance(sec.has_valid_ssh_key(), bool)
    assert sec.validate_connection("login2.fennec.meteo.dz", "sfoura") is True

    # CORRECTED: validate_connection() used to unconditionally return True
    # for ANY host/user, including empty strings or shell-metacharacter-
    # containing values - not a genuine validation despite the name.
    assert sec.validate_connection("", "sfoura") is False
    assert sec.validate_connection("login2.fennec.meteo.dz", "") is False
    assert sec.validate_connection("host; rm -rf /", "sfoura") is False
    assert sec.validate_connection("login2.fennec.meteo.dz", "user`whoami`") is False


def test_environment_manager():
    env = EnvironmentManager()
    res = env.setup_environment(["gcc/12.2.0", "eccodes/2.30.0", "openmpi/4.1.5"])
    assert "loaded_modules" in res

    # CORRECTED: "loaded_modules" used to unconditionally list every
    # REQUESTED module name regardless of whether `module load` genuinely
    # succeeded remotely - get_loaded_modules()'s own docstring promises
    # "active" modules, not merely requested ones. In this offline test
    # environment (no real FENNEC SSH transport), no load can genuinely
    # be confirmed, so it must honestly report none loaded rather than
    # echo back the request.
    assert res["load_success"] is False
    assert res["loaded_modules"] == []

    # CORRECTED: ModuleLoader.discover_modules() used to run `module
    # avail` and then completely discard its result, returning a
    # hardcoded catalog as if it had genuinely been discovered.
    discovered = env.module_loader.discover_modules()
    assert discovered["is_real_data"] is False
    assert "compilers" in discovered  # honest labeled fallback catalog, not live detection


def test_paramiko_ssh_and_executor():
    ssh = SSHConnector(hostname=OFFLINE_TEST_HOSTNAME, username="sfoura")
    assert ssh.connect() is True
    assert ssh.is_alive() is True
    executor = RemoteExecutor(ssh)
    res = executor.execute_command("echo 'FENNEC HPC OPERATIONAL'")
    assert res["exit_code"] == 0
    assert "execution_time" in res
    assert ssh.disconnect() is True


def test_is_real_connection_false_when_authentication_fails(monkeypatch):
    """
    Regression test for a real user-reported bug: the ESOC status bar showed
    "HPC: Connected" for a connection whose authentication had genuinely
    failed (root cause: a saved connection profile with a malformed username
    field, e.g. "user@host" typed by habit from `ssh user@host` syntax).

    SSHConnector.is_real_connection used to be computed from
    Transport.is_active() alone - which paramiko keeps True for an open
    TCP/SSH transport even after AuthenticationException, because
    SSHClient.connect() does not close the transport on an auth failure.
    This mocks exactly that scenario (transport up, authentication refused)
    without any real network access, and asserts is_real_connection is now
    correctly False - it must require Transport.is_authenticated(), not
    just is_active().
    """
    import paramiko

    class _FakeTransport:
        def is_active(self):
            return True  # the TCP/SSH transport really is still open...

        def is_authenticated(self):
            return False  # ...but authentication genuinely failed.

    class _FakeSSHClient:
        def set_missing_host_key_policy(self, policy):
            pass

        def connect(self, **kwargs):
            raise paramiko.AuthenticationException("Authentication failed (mocked - no real network access).")

        def get_transport(self):
            return _FakeTransport()

    monkeypatch.setattr(paramiko, "SSHClient", _FakeSSHClient)
    # getaddrinfo() is called before client.connect() to check DNS - fake it
    # resolving so the test exercises the post-connect transport check, not
    # the (separately tested) DNS-failure path. No real socket I/O occurs.
    monkeypatch.setattr(
        "socket.getaddrinfo", lambda *a, **kw: [(2, 1, 6, "", (OFFLINE_TEST_HOSTNAME, 22))]
    )

    ssh = SSHConnector(hostname=OFFLINE_TEST_HOSTNAME, username="sfoura@10.16.20.2")
    assert ssh.connect() is True  # offline-dev-mode convention: still returns True, never crashes the caller
    assert ssh.is_real_connection is False  # the bug: this used to be True


def test_file_transfer_manager_honest_status_when_no_real_sftp(tmp_path):
    """
    CORRECTED: SSHConnector.upload()/download() and
    FileTransferManager.sync_files()/download_results() used to
    unconditionally return True / record "status": "COMPLETED" even when
    no SFTP channel could be opened - the default outcome in this offline
    development environment (no real FENNEC connectivity). Now honestly
    reports failure instead of a fabricated success.
    """
    ssh = SSHConnector(hostname=OFFLINE_TEST_HOSTNAME, username="sfoura")
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
    ssh = SSHConnector(hostname=OFFLINE_TEST_HOSTNAME, username="sfoura")
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
    # CORRECTED: was "university_hpc", a profile name that doesn't
    # exist in config/hpc.yaml - this test's own name ("fennec_workflow")
    # already gave away that "fennec" was always the real target;
    # get_cluster_profile() used to silently substitute it anyway via
    # its now-removed arbitrary-fallback behavior.
    #
    # CORRECTED (later): connect() resolves "fennec"'s real hostname
    # (login2.fennec.meteo.dz) from config/hpc.yaml - on this
    # ONM-networked machine that is a real, reachable address (see
    # OFFLINE_TEST_HOSTNAME's own comment above). The `overrides`
    # hostname (connect()'s own parameter, added alongside the Connection
    # Wizard fix) lets this test still exercise real "fennec" PROFILE
    # NAME resolution (scheduler/module/Python discovery from
    # config/hpc.yaml) without the actual TCP/SSH attempt ever leaving
    # this machine.
    assert hpc.connect("fennec", overrides={"hostname": OFFLINE_TEST_HOSTNAME}) is True
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

    # One-Click ALADIN pipeline test (docs/ACF_HPC_005_NEXT_ROADMAP.md's
    # CI/CD objective names "AROME 1.3 km et ALADIN 7.5 km" together, but
    # only the AROME pipeline existed until now - added as a genuine
    # mirror of execute_one_click_arome(), same honesty contract.
    aladin_res = hpc.execute_one_click_aladin()
    assert aladin_res["is_real_submission"] is False
    assert aladin_res["status"] != "SUCCESS"
    assert aladin_res["operational_model"] == "ALADIN-7.5km"
    assert "job_id" in aladin_res

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
