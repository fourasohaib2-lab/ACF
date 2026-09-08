"""HPC Workflow Archiving & Cleanup Engine (ACF-HPC-104).

NOTE (correction): WorkflowArchive.archive_results() used to ignore the
`files` list entirely (no file was ever copied/moved into
destination_dir - only the empty directory was created) and
WorkflowCleanup.cleanup_scratch() used to ignore `scratch_dir` entirely
and delete nothing, yet both unconditionally returned True as if the
archiving/cleanup had genuinely happened. Distinct from the real,
unrelated WorkflowEngine.archive_results() in workflow_engine.py (Stage
11 of the operational cycle, which does write a real archive file) -
this module's classes have no real caller anywhere in the codebase
(verified) beyond their own package re-export shims. Kept (not
deleted, per this session's standing rule); now performs the real
filesystem operation it already claimed to perform, and reports
failures honestly instead of masking them behind a hard-coded True.
"""

import os
import shutil


class WorkflowArchive:
    """Manages NetCDF, GRIB2, PNG, JSON result archiving."""

    def archive_results(self, files: list[str], destination_dir: str = "/tmp/acf_archive") -> bool:
        """Archive output result files to destination directory.

        NOTE (correction): used to ignore `files` completely - only the
        destination directory was created, no file was ever archived -
        and unconditionally returned True regardless. Now actually
        copies each file into destination_dir and returns True only if
        every file was copied successfully.
        """
        os.makedirs(destination_dir, exist_ok=True)
        if not files:
            return False
        success = True
        for file_path in files:
            try:
                shutil.copy2(file_path, destination_dir)
            except OSError:
                success = False
        return success


class WorkflowCleanup:
    """Cleans temporary scratch directories and temporary SLURM files."""

    def cleanup_scratch(self, scratch_dir: str = "/tmp/acf_scratch") -> bool:
        """Clean up temporary scratch directory.

        NOTE (correction): used to ignore `scratch_dir` completely and
        delete nothing, yet unconditionally returned True. Now actually
        removes the directory's contents (recreating it empty) and
        returns False if the directory does not exist or removal fails.
        """
        if not os.path.isdir(scratch_dir):
            return False
        try:
            shutil.rmtree(scratch_dir)
            os.makedirs(scratch_dir, exist_ok=True)
        except OSError:
            return False
        return True
