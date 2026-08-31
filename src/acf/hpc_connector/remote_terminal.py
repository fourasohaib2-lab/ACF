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
        """Invoke persistent interactive shell channel."""
        if self.connector.is_alive() and self.connector.client:
            try:
                self.channel = self.connector.client.invoke_shell()
                if self.channel is not None:
                    self.channel.settimeout(2.0)
                log_hpc_event("INFO", "Persistent Paramiko interactive shell channel opened.")
                return True
            except Exception as e:
                log_hpc_event("WARNING", f"Failed to invoke interactive shell: {e}")
        return True

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
