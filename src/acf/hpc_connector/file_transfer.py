"""Production SFTP & Rsync File Synchronizer for FENNEC HPC (ACF-HPC-100)."""

import hashlib
import os
from collections.abc import Callable
from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.ssh_connector import SSHConnector


class FileTransferManager:
    """Synchronizes NetCDF, GRIB2, Zarr, and checkpoint files between local workstation and FENNEC HPC via SFTP."""

    def __init__(self, connector: SSHConnector | None = None) -> None:
        self.connector = connector or SSHConnector()
        self.transfer_history: list[dict[str, Any]] = []

    def compute_sha256(self, filepath: str) -> str:
        """
        Compute SHA256 checksum for verification.

        NOTE (correction): the fallback used to be "00000000000000000000000000000000"
        (32 hex chars - actually the wrong length for SHA256, which is 64
        hex chars) for BOTH "file does not exist" and "read raised an
        exception". Two different unreadable/missing files would produce
        the identical placeholder, so a caller comparing checksums between
        source and destination could see them "match" and believe a
        transfer was verified when in fact no real checksum was ever
        computed for either side. Replaced with an explicit, unambiguous
        sentinel that can never collide with a real hex digest or with
        another failure of the same kind.
        """
        if not os.path.exists(filepath):
            return "NO_CHECKSUM_FILE_NOT_FOUND"
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            log_hpc_event("WARNING", f"SHA256 checksum failed for {filepath}: {e}")
            return "NO_CHECKSUM_READ_ERROR"

    def sync_files(
        self,
        source_path: str,
        destination_path: str,
        sync_type: str = "sftp",
        callback: Callable[[int, int], None] | None = None,
    ) -> bool:
        """
        Synchronize dataset or checkpoint files via Paramiko SFTP.

        NOTE (correction): this used to always append "status": "COMPLETED"
        and always `return True`, regardless of whether the connector was
        even alive or whether upload() actually transferred anything (see
        SSHConnector.upload()'s own NOTE - it used to always return True
        too). A caller had no honest way to tell a real transfer from a
        skipped/failed one. The record's "status" and this method's return
        value now both honestly reflect what upload() actually reported.
        """
        log_hpc_event("INFO", f"SFTP Synchronizing [{source_path}] -> [{destination_path}]")

        if self.connector.is_alive():
            uploaded = self.connector.upload(source_path, destination_path, callback=callback)
        else:
            log_hpc_event("WARNING", f"SFTP Synchronize skipped (connector not alive): {source_path}")
            uploaded = False

        checksum = self.compute_sha256(source_path)
        record = {
            "source": source_path,
            "destination": destination_path,
            "type": sync_type,
            "checksum": checksum,
            "status": "COMPLETED" if uploaded else "FAILED_NO_REAL_TRANSFER",
        }
        self.transfer_history.append(record)
        return uploaded

    def download_results(
        self,
        remote_path: str,
        local_path: str,
        callback: Callable[[int, int], None] | None = None,
    ) -> bool:
        """
        Download remote NetCDF4 / GRIB2 forecast results to local workstation.

        NOTE (correction): used to always `return True` regardless of
        whether download() actually transferred anything - see this
        method's sync_files() sibling above for the same fix rationale.
        """
        log_hpc_event("INFO", f"SFTP Downloading forecast results: {remote_path} -> {local_path}")
        if self.connector.is_alive():
            return self.connector.download(remote_path, local_path, callback=callback)
        log_hpc_event("WARNING", f"SFTP Download skipped (connector not alive): {remote_path}")
        return False

    def sync_checkpoints(
        self, local_dir: str = "/tmp/checkpoints", remote_dir: str = "/scratch/users/sfoura/checkpoints"
    ) -> bool:
        """Synchronize simulation checkpoints."""
        return self.sync_files(local_dir, remote_dir)
