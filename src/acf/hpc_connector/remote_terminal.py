"""Persistent Interactive Remote Terminal Shell over Paramiko SSH (ACF-HPC-100)."""

import time

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.ssh_connector import SSHConnector


class RemoteTerminalShell:
    """Persistent interactive SSH terminal channel executing commands over Paramiko."""

    def __init__(self, connector: SSHConnector | None = None) -> None:
        self.connector = connector or SSHConnector()
        self.channel = None

    def open_shell(self) -> bool:
        """
        Invoke persistent interactive shell channel.

        NOTE (correction): used to unconditionally `return True` even
        when self.connector.is_alive()/self.connector.client were
        falsy (no attempt made at all) or invoke_shell() raised (caught,
        logged as WARNING, then still fell through to `return True`) -
        same fake-success pattern already fixed this session for
        SSHConnector.upload()/download(). Since is_alive() is honestly
        True even in this offline dev environment (no real FENNEC
        transport - see SSHConnector.connect()'s own NOTE) while
        self.client is a real-but-unconnected paramiko.SSHClient(),
        invoke_shell() raising here is the default path in this
        environment, not a rare edge case. self.channel stays None on
        any failure; now returns True only when a real channel object
        was actually obtained.
        """
        if self.connector.is_alive() and self.connector.client:
            try:
                self.channel = self.connector.client.invoke_shell()
            except Exception as e:
                log_hpc_event("WARNING", f"Failed to invoke interactive shell: {e}")
                self.channel = None
        else:
            log_hpc_event("WARNING", "Cannot open interactive shell: no live SSH connection/client.")

        if self.channel is not None:
            self.channel.settimeout(2.0)
            log_hpc_event("INFO", "Persistent Paramiko interactive shell channel opened.")
            return True
        return False

    def send_command(self, cmd: str) -> str:
        """Send command to persistent shell and stream response."""
        if self.channel and not self.channel.closed:
            try:
                self.channel.send(cmd.strip() + "\n")
                time.sleep(0.3)
                output = ""
                while self.channel.recv_ready():
                    output += self.channel.recv(4096).decode("utf-8", errors="replace")
                return output
            except Exception:
                pass

        # Fallback via direct SSH execution
        res = self.connector.execute(cmd)
        return res.get("stdout", "")

    def close(self) -> None:
        """Close terminal channel."""
        if self.channel:
            try:
                self.channel.close()
            except Exception:
                pass
            self.channel = None
