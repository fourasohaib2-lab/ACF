"""
Real, in-process Paramiko SSH/SFTP server tests for acf.hpc_connector -
added while investigating the user request "vérifier aussi la
connexion et l'importation des données depuis HPC" (also verify the
HPC connection and data import).

The existing tests/test_hpc_connector.py deliberately exercises only
the OFFLINE/no-real-transport honest-degradation path (this project's
real production target, FENNEC, is a private cluster this session has
no credentials for and cannot fabricate a connection to - same
"cannot fabricate real infrastructure access" discipline already
applied to RESTOR/live NWP data this session). It never proves the
GENUINE SUCCESS path - a real, authenticated Paramiko SSH session with
real command execution and real SFTP transfer - actually works.

This file closes that gap with a real (not mocked) in-process
Paramiko SSH+SFTP server, using only paramiko itself (already a real,
declared project dependency) - no new dependency, no OS-level sshd, no
root privileges, fully portable to any machine/CI runner. A real RSA
keypair is generated per test session; the server genuinely performs
the SSH transport handshake, public-key authentication, command
execution (via a real local subprocess) and SFTP get/put (via a real
temp directory) - the exact same real Paramiko protocol code paths a
genuine connection to FENNEC would exercise, just looped back to
127.0.0.1 instead of a real remote cluster.
"""

from __future__ import annotations

import os
import socket
import subprocess
import threading
from pathlib import Path

import paramiko
import pytest

from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.hpc_connector.file_transfer import FileTransferManager
from acf.hpc_connector.ssh_connector import SSHConnector

# --------------------------------------------------------------------- real in-process SSH+SFTP server


class _RealSFTPHandle(paramiko.SFTPHandle):
    def stat(self):
        return paramiko.SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))


class _RealSFTPServer(paramiko.SFTPServerInterface):
    """Real SFTP operations against a real local directory (``root``) -
    every ``put``/``get`` genuinely reads/writes real bytes on disk,
    nothing is simulated."""

    def __init__(self, server, root: Path, *args, **kwargs):
        super().__init__(server, *args, **kwargs)
        self.root = root

    def _real_path(self, path: str) -> str:
        return str(self.root / path.lstrip("/"))

    def open(self, path, flags, attr):
        real_path = self._real_path(path)
        os.makedirs(os.path.dirname(real_path), exist_ok=True)
        mode = "wb" if flags & (os.O_WRONLY | os.O_CREAT) else "rb"
        try:
            fh = open(real_path, mode)
        except OSError as exc:
            return paramiko.SFTPServer.convert_errno(exc.errno)
        handle = _RealSFTPHandle(flags)
        handle.readfile = fh
        handle.writefile = fh
        return handle

    def list_folder(self, path):
        real_path = self._real_path(path)
        try:
            return [paramiko.SFTPAttributes.from_stat(os.stat(real_path / Path(name))) for name in os.listdir(real_path)]
        except OSError as exc:
            return paramiko.SFTPServer.convert_errno(exc.errno)

    def stat(self, path):
        try:
            return paramiko.SFTPAttributes.from_stat(os.stat(self._real_path(path)))
        except OSError as exc:
            return paramiko.SFTPServer.convert_errno(exc.errno)

    lstat = stat

    def remove(self, path):
        try:
            os.remove(self._real_path(path))
            return paramiko.SFTP_OK
        except OSError as exc:
            return paramiko.SFTPServer.convert_errno(exc.errno)


class _RealSSHServer(paramiko.ServerInterface):
    """Real SSH server - genuinely validates the client's real public
    key against the one real keypair this test session generated, and
    genuinely runs an exec_command's real command via subprocess."""

    def __init__(self, authorized_public_key: paramiko.PKey) -> None:
        self._authorized_key = authorized_public_key
        self.exec_command_received: list[str] = []

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username: str) -> str:
        return "publickey"

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        if key.get_base64() == self._authorized_key.get_base64():
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel: paramiko.Channel, command: bytes) -> bool:
        self.exec_command_received.append(command.decode())
        real_result = subprocess.run(command.decode(), shell=True, capture_output=True)
        channel.send(real_result.stdout)
        channel.send_stderr(real_result.stderr)
        channel.send_exit_status(real_result.returncode)
        threading.Timer(0.05, channel.close).start()
        return True


class _RealSSHTestServer:
    """Owns one real listening TCP socket + one real Paramiko SSH
    transport per accepted connection, backed by a real temp
    directory for SFTP."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.host_key = paramiko.RSAKey.generate(2048)
        self.client_key = paramiko.RSAKey.generate(2048)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("127.0.0.1", 0))
        self._socket.listen(1)
        self.port = self._socket.getsockname()[1]

        self._server_iface = _RealSSHServer(self.client_key)
        self._thread = threading.Thread(target=self._serve_one, daemon=True)
        self._thread.start()

    def _serve_one(self) -> None:
        try:
            client_sock, _ = self._socket.accept()
        except OSError:
            return
        transport = paramiko.Transport(client_sock)
        transport.add_server_key(self.host_key)
        transport.set_subsystem_handler("sftp", paramiko.SFTPServer, sftp_si=_RealSFTPServer, root=self.root)
        transport.start_server(server=self._server_iface)
        channel = transport.accept(10)
        if channel is not None:
            # Real command execution already handled by check_channel_exec_request;
            # keep the transport alive briefly so the client can finish reading.
            import time

            time.sleep(0.3)

    def client_key_path(self, tmp_path: Path) -> Path:
        path = tmp_path / "test_client_key"
        self.client_key.write_private_key_file(str(path))
        return path

    def close(self) -> None:
        try:
            self._socket.close()
        except OSError:
            pass


@pytest.fixture
def real_ssh_server(tmp_path):
    server_root = tmp_path / "remote_root"
    server_root.mkdir()
    server = _RealSSHTestServer(server_root)
    yield server
    server.close()


# --------------------------------------------------------------------- SSHConnector


def test_ssh_connector_genuinely_authenticates_over_a_real_transport(real_ssh_server, tmp_path):
    key_path = real_ssh_server.client_key_path(tmp_path)

    conn = SSHConnector(
        hostname="127.0.0.1", username="testuser", port=real_ssh_server.port, key_filename=str(key_path), timeout=5.0
    )
    connected = conn.connect()

    assert connected is True
    assert conn.is_real_connection is True  # a real, authenticated transport - not the offline fallback
    assert conn.is_alive() is True

    conn.disconnect()


def test_ssh_connector_executes_a_real_remote_command(real_ssh_server, tmp_path):
    key_path = real_ssh_server.client_key_path(tmp_path)
    conn = SSHConnector(
        hostname="127.0.0.1", username="testuser", port=real_ssh_server.port, key_filename=str(key_path), timeout=5.0
    )
    conn.connect()

    result = conn.execute("echo REAL_SSH_OUTPUT_42")

    assert result["is_simulated"] is False
    assert result["exit_code"] == 0
    assert "REAL_SSH_OUTPUT_42" in result["stdout"]
    conn.disconnect()


# --------------------------------------------------------------------- FileTransferManager (real SFTP)


def test_file_transfer_manager_uploads_and_downloads_real_bytes(real_ssh_server, tmp_path):
    key_path = real_ssh_server.client_key_path(tmp_path)
    conn = SSHConnector(
        hostname="127.0.0.1", username="testuser", port=real_ssh_server.port, key_filename=str(key_path), timeout=5.0
    )
    conn.connect()
    conn.open_sftp()

    local_src = tmp_path / "real_input.grib2"
    local_src.write_bytes(b"REAL-BYTES-FOR-A-REAL-SFTP-TRANSFER" * 500)

    manager = FileTransferManager(conn)
    uploaded = manager.sync_files(str(local_src), "/incoming/real_input.grib2")

    assert uploaded is True
    assert manager.transfer_history[-1]["status"] == "COMPLETED"
    remote_file = real_ssh_server.root / "incoming" / "real_input.grib2"
    assert remote_file.exists()
    assert remote_file.read_bytes() == local_src.read_bytes()  # real, byte-for-byte real transfer

    local_dst = tmp_path / "downloaded_output.grib2"
    downloaded = manager.download_results("/incoming/real_input.grib2", str(local_dst))

    assert downloaded is True
    assert local_dst.read_bytes() == local_src.read_bytes()  # real round-trip integrity

    conn.disconnect()


# --------------------------------------------------------------------- HPCConnectionManager (full workflow)


def test_hpc_connection_manager_completes_a_real_connect_workflow(real_ssh_server, tmp_path, monkeypatch):
    """The real, full 11-step HPCConnectionManager.connect() workflow
    (hostname/whoami/pwd verification, cluster/scheduler/Python
    detection, module loads) run against a real, authenticated SSH
    transport - not the offline fallback the rest of
    tests/test_hpc_connector.py exercises."""
    key_path = real_ssh_server.client_key_path(tmp_path)
    monkeypatch.chdir(tmp_path)

    manager = HPCConnectionManager()
    connected = manager.connect(
        profile_name="real_test_server",
        overrides={
            "hostname": "127.0.0.1",
            "username": "testuser",
            "port": real_ssh_server.port,
            "key_path": str(key_path),
            "timeout": 5.0,
        },
    )

    assert connected is True
    assert manager.is_connected is True
    assert manager.ssh_connector.is_real_connection is True

    manager.disconnect()
    assert manager.is_connected is False
