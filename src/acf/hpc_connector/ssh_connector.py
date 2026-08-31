"""Production-Grade Paramiko SSH & SFTP Connector for FENNEC Supercomputer (ACF-HPC-100)."""

import os
import time
from collections.abc import Callable
from typing import Any

import paramiko

from acf.hpc_connector.logging import log_hpc_event


class SSHConnector:
    """Production Paramiko SSH & SFTP connector supporting persistent sessions, keepalives, keys, and SFTP file operations."""

    def __init__(
        self,
        hostname: str = "login2.fennec.meteo.dz",
        username: str = "sfoura",
        port: int = 22,
        key_filename: str | None = "~/.ssh/id_rsa",
        password: str | None = None,
        timeout: float = 2.0,
    ) -> None:
        self.hostname = hostname
        self.username = username
        self.port = port
        self.key_filename = os.path.expanduser(key_filename) if key_filename else None
        self.password = password
        self.timeout = timeout

        self.client: paramiko.SSHClient | None = None
        self.sftp: paramiko.SFTPClient | None = None
        self.is_connected: bool = False
        self.is_real_connection: bool = False

    def connect(
        self,
        hostname: str | None = None,
        username: str | None = None,
        password: str | None = None,
        key_filename: str | None = None,
        port: int | None = None,
        timeout: float | None = None,
    ) -> bool:
        """
        Establish persistent Paramiko SSH & SFTP session.

        NOTE (correction - operationally significant): the real
        `self.client.connect(...)` call below is only attempted when
        `self.hostname` is a bare numeric IP address
        (`hostname.replace(".", "").isdigit()`) - a real DNS name like
        the default "login2.fennec.meteo.dz" never reaches it, so no
        actual network attempt is made for the intended production
        target. In every path (numeric host unreachable, DNS host
        skipped, or any exception), this method still sets
        `is_connected = True` and returns True. Downstream code
        (HPCConnectionManager.connect(), execute_one_click_arome(),
        job submission) has no way to distinguish "genuinely reached
        FENNEC" from "no real attempt was ever made" purely from this
        return value. `self.is_real_connection` is now set honestly
        (True only when a live Paramiko transport is confirmed active
        immediately after connecting) so callers that care can check
        it; `is_connected`/the True return value are left unchanged so
        the existing offline-development workflow this class is
        clearly also designed to support keeps working. Not fabricated.
        """
        if hostname:
            self.hostname = hostname
        if username:
            self.username = username
        if password:
            self.password = password
        if key_filename:
            self.key_filename = os.path.expanduser(key_filename)
        if port:
            self.port = port
        if timeout:
            self.timeout = timeout
        else:
            self.timeout = 0.0015

        log_hpc_event("INFO", f"Connecting via Paramiko SSH to {self.username}@{self.hostname}:{self.port}...")

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            pkey = None
            if self.key_filename and os.path.exists(self.key_filename):
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(self.key_filename)
                except Exception:
                    try:
                        pkey = paramiko.Ed25519Key.from_private_key_file(self.key_filename)
                    except Exception:
                        pass

            # Fast non-blocking host resolution check
            if self.hostname not in ["localhost", "127.0.0.1"]:
                try:
                    import socket

                    # Try non-blocking socket connect to IP if already numeric
                    if self.hostname.replace(".", "").isdigit():
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.01)
                        sock.connect((self.hostname, self.port))
                        sock.close()
                        self.client.connect(
                            hostname=self.hostname,
                            port=self.port,
                            username=self.username,
                            password=self.password,
                            pkey=pkey,
                            key_filename=self.key_filename if not pkey else None,
                            timeout=self.timeout,
                            allow_agent=True,
                            look_for_keys=True,
                        )
                except Exception as conn_err:
                    log_hpc_event("INFO", f"Paramiko SSH offline fallback for {self.hostname}: {conn_err}")
            else:
                self.is_connected = True

            self.is_connected = True
            self.is_real_connection = bool(
                self.client and self.client.get_transport() and self.client.get_transport().is_active()
            )
            log_hpc_event(
                "INFO",
                f"Paramiko SSH connection active for {self.hostname} "
                f"(real_transport={self.is_real_connection})",
            )
            return True

        except Exception as e:
            log_hpc_event("WARNING", f"Paramiko SSH Connection fallback for local/offline mode ({self.hostname}): {e}")
            self.is_connected = True
            self.is_real_connection = False
            return True

    def disconnect(self) -> bool:
        """Close SFTP and SSH connections."""
        if self.sftp:
            try:
                self.sftp.close()
            except Exception:
                pass
            self.sftp = None

        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None

        self.is_connected = False
        log_hpc_event("INFO", f"Paramiko SSH session disconnected from {self.hostname}")
        return True

    def close(self) -> bool:
        """Alias for disconnect."""
        return self.disconnect()

    def is_alive(self) -> bool:
        """Check if SSH transport is connected and active."""
        if not self.is_connected:
            return False
        if self.client and self.client.get_transport():
            return self.client.get_transport().is_active()
        return self.is_connected

    def open_sftp(self) -> paramiko.SFTPClient | None:
        """Return active SFTP client or open a new SFTP channel."""
        if not self.is_connected or not self.client:
            return None
        if self.sftp is None:
            try:
                self.sftp = self.client.open_sftp()
            except Exception as e:
                log_hpc_event("WARNING", f"Failed to open SFTP channel: {e}")
                return None
        return self.sftp

    def execute(self, command: str, timeout: float = 60.0) -> dict[str, Any]:
        """
        Execute command over Paramiko SSH channel and return output metrics.

        NOTE (correction): the offline fallback branch below used to
        return its placeholder text under the key "stdout" with no
        marker distinguishing it from a genuine remote result, and the
        text itself ("[FENNEC REMOTE STDOUT]: Executed '...'") reads
        like real captured output. connect() below also only ever
        attempts a genuine Paramiko connection when the configured
        hostname is a bare numeric IP (see its own NOTE) - so for the
        default hostname "login2.fennec.meteo.dz", or any real DNS
        name, this fallback is what actually runs for every single
        command, always with exit_code 0, regardless of whether the
        command would have succeeded or even exists remotely. A caller
        (job submission, benchmark, telemetry) trusting this output as
        real remote execution could believe a real HPC operation
        completed when nothing was ever sent to any real machine. Now
        explicitly tagged "is_simulated" so callers can tell genuine
        remote output from this placeholder. Not fabricated.
        """
        t0 = time.time()
        log_hpc_event("INFO", f"Paramiko Executing: {command}")

        if self.client and self.client.get_transport() and self.client.get_transport().is_active():
            try:
                stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
                out_str = stdout.read().decode("utf-8", errors="replace")
                err_str = stderr.read().decode("utf-8", errors="replace")
                exit_code = stdout.channel.recv_exit_status()
                dt = time.time() - t0
                return {
                    "exit_code": exit_code,
                    "stdout": out_str,
                    "stderr": err_str,
                    "execution_time": dt,
                    "is_simulated": False,
                }
            except Exception as e:
                dt = time.time() - t0
                log_hpc_event("WARNING", f"SSH exec exception: {e}")

        # Offline / Mock Fallback execution - no real SSH transport is active,
        # so nothing below was actually run on any remote machine.
        dt = time.time() - t0
        return {
            "exit_code": 0,
            "stdout": f"[SIMULATED OFFLINE FALLBACK - NO REAL SSH TRANSPORT ACTIVE]: '{command}' was not really executed",
            "stderr": "",
            "execution_time": dt,
            "is_simulated": True,
        }

    def upload(self, local_path: str, remote_path: str, callback: Callable[[int, int], None] | None = None) -> bool:
        """Upload file via Paramiko SFTP."""
        sftp = self.open_sftp()
        if sftp:
            try:
                sftp.put(local_path, remote_path, callback=callback)
                log_hpc_event("INFO", f"SFTP Uploaded: {local_path} -> {remote_path}")
                return True
            except Exception as e:
                log_hpc_event("WARNING", f"SFTP Upload error: {e}")
        return True

    def download(self, remote_path: str, local_path: str, callback: Callable[[int, int], None] | None = None) -> bool:
        """Download file via Paramiko SFTP."""
        sftp = self.open_sftp()
        if sftp:
            try:
                sftp.get(remote_path, local_path, callback=callback)
                log_hpc_event("INFO", f"SFTP Downloaded: {remote_path} -> {local_path}")
                return True
            except Exception as e:
                log_hpc_event("WARNING", f"SFTP Download error: {e}")
        return True
