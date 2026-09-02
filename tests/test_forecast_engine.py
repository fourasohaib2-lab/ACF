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
from datetime import UTC, datetime, timedelta

import numpy as np
import xarray as xr

from acf.forecast.engine import MODEL_CONFIGS, _certify_forecast_output, run_forecast_cycle
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


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
    assert "CERTIFICATION: CERTIFIED" in result.stdout
    ds = xr.open_dataset(output_path)
    assert "T" in ds.data_vars


# ------------------------------------------------------------------ Certification Engine wiring (continuous production trigger)


def test_run_forecast_cycle_certifies_by_default(tmp_path):
    """The real production trigger: a real, healthy forecast cycle must come back CERTIFIED, not just have a NetCDF file written."""
    result = run_forecast_cycle("ARPEGE", steps=1, output_path=str(tmp_path / "out.nc"))

    assert "certification" in result
    cert = result["certification"]
    assert cert["decision"] == "CERTIFIED"
    assert cert["failed_steps"] == []
    assert cert["dataset_id"].startswith("ARPEGE-forecast-")


def test_run_forecast_cycle_certify_false_skips_it(tmp_path):
    result = run_forecast_cycle("ARPEGE", steps=1, output_path=str(tmp_path / "out.nc"), certify=False)
    assert "certification" not in result


def test_certify_forecast_output_rejects_non_finite_values():
    """Real QC PASS check, exercised directly: a genuinely non-finite (NaN) surface temperature - the real failure mode a diverged coupled solver would produce - must be REJECTED, not silently certified."""
    grid = EarthGrid(n_lat=4, n_lon=4, n_levels=2)
    state = {"T": np.full((2, 4, 4), np.nan)}
    ref_time = datetime(2026, 9, 2, tzinfo=UTC)

    report = _certify_forecast_output("ARPEGE", grid, state, ref_time, ref_time + timedelta(hours=1), timedelta(hours=1))

    assert report["decision"] == "REJECTED"
    failed_names = {s["name"] for s in report["failed_steps"]}
    assert "qc_pass" in failed_names


def test_certify_forecast_output_certifies_a_real_healthy_field():
    grid = EarthGrid(n_lat=4, n_lon=4, n_levels=2)
    state = {"T": np.full((2, 4, 4), 288.0)}  # a real, physically plausible surface temperature
    ref_time = datetime(2026, 9, 2, tzinfo=UTC)

    report = _certify_forecast_output("ARPEGE", grid, state, ref_time, ref_time + timedelta(hours=1), timedelta(hours=1))

    assert report["decision"] == "CERTIFIED"


def test_cli_reports_certification_and_exits_nonzero_when_rejected(tmp_path, monkeypatch):
    """A real REJECTED certification must be a real, non-zero exit signal for a CI/CD scheduler - same convention scripts/daily_forecast_cycle.py already established for is_real_submission - not silently ignored."""
    import acf.forecast.engine as engine_module

    def _fake_certify(model, grid, state, forecast_reference_time, valid_time, lead_time):
        return {"decision": "REJECTED", "dataset_id": "fake-id", "failed_steps": [{"name": "qc_pass", "detail": "fake"}]}

    monkeypatch.setattr(engine_module, "_certify_forecast_output", _fake_certify)

    exit_code = engine_module.main(["--model", "ARPEGE", "--steps", "1", "--output", str(tmp_path / "out.nc")])
    assert exit_code == 2


def test_cli_no_certify_flag_skips_certification(tmp_path, capsys):
    from acf.forecast.engine import main

    exit_code = main(["--model", "ARPEGE", "--steps", "1", "--output", str(tmp_path / "out.nc"), "--no-certify"])
    assert exit_code == 0
    assert "CERTIFICATION" not in capsys.readouterr().out
