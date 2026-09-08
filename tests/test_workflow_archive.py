"""
Unit test suite for hpc_workflow.workflow_archive's WorkflowArchive and
WorkflowCleanup classes (ACF-HPC-104).

REWRITTEN: archive_results() used to ignore the `files` list entirely
(no file was ever copied - only the destination directory was created)
and cleanup_scratch() used to ignore `scratch_dir` entirely and delete
nothing, yet both unconditionally returned True. Distinct from the
real, unrelated WorkflowEngine.archive_results() in workflow_engine.py
(covered by tests/test_workflow_engine.py), which is a genuinely real
Stage-11 archiving method. See workflow_archive.py's NOTE (correction)
docstrings for what each used to fabricate.
"""

import os

from acf.hpc_workflow.workflow_archive import WorkflowArchive, WorkflowCleanup


def test_archive_results_copies_real_files(tmp_path):
    src_file = tmp_path / "output.grib2"
    src_file.write_text("fake grib2 payload")
    dest_dir = tmp_path / "archive"

    ok = WorkflowArchive().archive_results([str(src_file)], destination_dir=str(dest_dir))

    assert ok is True
    archived = dest_dir / "output.grib2"
    assert archived.exists()
    assert archived.read_text() == "fake grib2 payload"


def test_archive_results_no_longer_claims_success_for_empty_input():
    """CORRECTED: used to return True even with an empty `files` list and nothing archived."""
    assert WorkflowArchive().archive_results([]) is False


def test_archive_results_reports_failure_for_missing_source_file(tmp_path):
    dest_dir = tmp_path / "archive"
    missing = tmp_path / "does_not_exist.nc"

    ok = WorkflowArchive().archive_results([str(missing)], destination_dir=str(dest_dir))

    assert ok is False


def test_cleanup_scratch_actually_removes_contents(tmp_path):
    scratch_dir = tmp_path / "scratch"
    scratch_dir.mkdir()
    (scratch_dir / "leftover.tmp").write_text("stale slurm output")

    ok = WorkflowCleanup().cleanup_scratch(scratch_dir=str(scratch_dir))

    assert ok is True
    assert os.path.isdir(scratch_dir)
    assert list(scratch_dir.iterdir()) == []


def test_cleanup_scratch_no_longer_claims_success_for_missing_directory(tmp_path):
    """CORRECTED: used to unconditionally return True even if `scratch_dir` never existed."""
    missing_dir = tmp_path / "never_created"
    assert WorkflowCleanup().cleanup_scratch(scratch_dir=str(missing_dir)) is False
