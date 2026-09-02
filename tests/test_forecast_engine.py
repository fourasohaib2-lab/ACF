"""
Tests for acf.forecast.engine - the real CLI entry point
HPCConnectionManager's one-click AROME/ALADIN pipelines submit as a
SLURM job command. Did not exist before this fix (docs/
ACF_HPC_005_NEXT_ROADMAP.md's CI/CD objective) - even a successfully
submitted real job would have failed immediately with
ModuleNotFoundError.
"""

import subprocess
import sys

import xarray as xr

from acf.forecast.engine import MODEL_CONFIGS, run_forecast_cycle


def test_model_configs_cover_both_operational_models():
    # ARPEGE added 2026-09-02 for real multi-model disagreement
    # (ModelConsensusEngine.compute_real_multi_model_disagreement()).
    assert set(MODEL_CONFIGS) == {"AROME", "ALADIN", "ARPEGE"}
    assert MODEL_CONFIGS["AROME"]["resolution_km"] == 1.3
    assert MODEL_CONFIGS["ALADIN"]["resolution_km"] == 7.5
    assert MODEL_CONFIGS["ARPEGE"]["resolution_km"] == 10.0


def test_run_forecast_cycle_arpege_uses_its_own_global_scale_grid(tmp_path):
    output_path = str(tmp_path / "arpege_output.nc")
    result = run_forecast_cycle("ARPEGE", steps=1, output_path=output_path)

    assert result["status"] == "SUCCESS"
    assert result["operational_resolution_km"] == 10.0

    ds = xr.open_dataset(output_path)
    assert ds.sizes["latitude"] == MODEL_CONFIGS["ARPEGE"]["n_lat"]
    assert ds.sizes["longitude"] == MODEL_CONFIGS["ARPEGE"]["n_lon"]


def test_run_forecast_cycle_arome_writes_real_netcdf(tmp_path):
    output_path = str(tmp_path / "arome_output.nc")
    result = run_forecast_cycle("AROME", steps=2, dt_seconds=60.0, output_path=output_path)

    assert result["status"] == "SUCCESS"
    assert result["model"] == "AROME"
    assert result["steps_completed"] == 2
    assert result["output_path"] == output_path

    ds = xr.open_dataset(output_path)
    assert "T" in ds.data_vars
    assert "P" in ds.data_vars
    assert ds.attrs["time_step"] == 2
    assert ds.attrs["conventions"] == "CF-1.8"


def test_run_forecast_cycle_aladin_uses_its_own_grid(tmp_path):
    output_path = str(tmp_path / "aladin_output.nc")
    result = run_forecast_cycle("ALADIN", steps=1, output_path=output_path)

    assert result["status"] == "SUCCESS"
    assert result["operational_resolution_km"] == 7.5

    ds = xr.open_dataset(output_path)
    assert ds.sizes["latitude"] == MODEL_CONFIGS["ALADIN"]["n_lat"]
    assert ds.sizes["longitude"] == MODEL_CONFIGS["ALADIN"]["n_lon"]


def test_unknown_model_raises():
    import pytest

    with pytest.raises(ValueError):
        run_forecast_cycle("UNKNOWN_MODEL")


def test_real_cli_invocation_matches_what_the_slurm_batch_script_runs(tmp_path):
    """This is the exact command HPCConnectionManager.execute_one_click_arome()
    generates for the SLURM batch script - run for real as a subprocess
    (not just calling the Python function directly) to prove
    `python -m acf.forecast.engine --model AROME` genuinely works as an
    entry point, which is the whole point of this fix."""
    output_path = str(tmp_path / "cli_output.nc")
    result = subprocess.run(
        [sys.executable, "-m", "acf.forecast.engine", "--model", "AROME", "--steps", "1", "--output", output_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "SUCCESS" in result.stdout
    ds = xr.open_dataset(output_path)
    assert "T" in ds.data_vars
