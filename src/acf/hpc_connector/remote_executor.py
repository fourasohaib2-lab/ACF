"""Production Remote Executor via Paramiko SSH (ACF-HPC-100)."""

import time
from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.ssh_connector import SSHConnector


class RemoteExecutor:
    """Executes remote HPC commands strictly over Paramiko SSH without local subprocess invocations."""

    def __init__(self, connector: SSHConnector | None = None) -> None:
        self.connector = connector or SSHConnector()

    def execute_command(self, cmd: str, timeout: float = 120.0) -> dict[str, Any]:
        """Execute command remotely via Paramiko SSH channel and return structured results dictionary."""
        t0 = time.time()
        log_hpc_event("INFO", f"Executing Remote Command: {cmd}")

        res = self.connector.execute(cmd, timeout=timeout)
        execution_time = res.get("execution_time", time.time() - t0)

        return {
            "exit_code": res.get("exit_code", 0),
            "stdout": res.get("stdout", ""),
            "stderr": res.get("stderr", ""),
            "execution_time": execution_time,
            # NOTE (correction): propagates SSHConnector.execute()'s
            # honest "is_simulated" marker (see its docstring) instead
            # of silently dropping it - callers of this class had no
            # way to tell genuine remote output from the offline
            # fallback placeholder. Defaults True (simulated) if the
            # connector doesn't report it, which is the safe assumption.
            "is_simulated": res.get("is_simulated", True),
        }
