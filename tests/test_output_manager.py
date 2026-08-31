"""
Unit test suite for HPCOutputManager (ACF-HPC-004).
"""

from pathlib import Path

from acf.hpc_connector.output_manager import HPCOutputManager


def test_initialize_and_save_metadata(tmp_path: Path):
    """Test initializing run directory and saving JSON metadata."""
    manager = HPCOutputManager(base_dir=str(tmp_path))
    run_id = "test_run_001"

    subdirs = manager.initialize_run_directory(run_id)
    assert Path(subdirs["outputs"]).exists()
    assert Path(subdirs["forecasts"]).exists()

    meta_file = manager.save_metadata(run_id, {"model": "AROME", "status": "SUCCESS"})
    assert Path(meta_file).exists()

    files = manager.list_run_files(run_id, "forecasts")
    assert isinstance(files, list)
