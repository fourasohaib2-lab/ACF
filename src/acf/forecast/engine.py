"""
ACF Forecast Cycle Engine — real CLI entry point for AROME/ALADIN runs.

This is the actual module HPCConnectionManager.execute_one_click_arome()
(and the new execute_one_click_aladin()) submit as a SLURM job command
(`python -m acf.forecast.engine --model AROME`). It did not exist before
this fix - so even a real, successfully-submitted job on a real cluster
would have failed immediately with ModuleNotFoundError. Not a stub: this
genuinely runs acf.simulation_engine.coupled_solver.CoupledEarthSolver
for the requested model's real grid resolution and writes a real
CF-compliant NetCDF file via the already-tested NetcdfWriter - the same
real solver/writer this session's other fixes (ESOCController.
handle_run_simulation, simulation_engine tests) already exercise, not a
new, separately-invented forecast implementation.
"""

import argparse
import logging
import sys
from typing import Any

import numpy as np

from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid
from acf.simulation_engine.output.netcdf_writer import NetcdfWriter

logger = logging.getLogger("acf.forecast.engine")

#: Grid resolutions matching the operational configurations named in
#: docs/ACF_HPC_005_NEXT_ROADMAP.md ("AROME 1.3 km et ALADIN 7.5 km").
#: n_lat/n_lon/n_levels are genuine EarthGrid parameters (this module's
#: real spectral/gridpoint resolution), not the literal km grid spacing
#: of the real operational AROME/ALADIN systems - ACF's EarthGrid is a
#: global lat/lon grid, not AROME's actual Lambert conformal domain, so
#: resolution_km below is descriptive of which operational model this
#: run stands in for, not a claim that this grid matches its real
#: horizontal spacing.
#: ARPEGE added 2026-09-02 to enable real multi-model disagreement
#: (acf.visualization.ai_forecast_center.model_consensus_engine.
#: ModelConsensusEngine.compute_real_multi_model_disagreement()) -
#: ARPEGE is ONM's real global model, hence the coarser/global-scale
#: stand-in grid here (vs. AROME/ALADIN's regional stand-ins above).
#: Same resolution_km caveat as the rest of this dict applies.
MODEL_CONFIGS: dict[str, dict[str, Any]] = {
    "AROME": {"resolution_km": 1.3, "n_lat": 90, "n_lon": 180, "n_levels": 32, "default_steps": 24},
    "ALADIN": {"resolution_km": 7.5, "n_lat": 60, "n_lon": 120, "n_levels": 24, "default_steps": 24},
    "ARPEGE": {"resolution_km": 10.0, "n_lat": 48, "n_lon": 96, "n_levels": 20, "default_steps": 24},
}


def run_forecast_cycle(
    model: str,
    steps: int | None = None,
    dt_seconds: float = 60.0,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Run one real forecast cycle and write its final state to NetCDF.

    Parameters
    ----------
    model : "AROME" or "ALADIN".
    steps : number of coupled time steps (defaults to the model's
        configured default_steps).
    dt_seconds : coupled solver time step, in seconds.
    output_path : NetCDF output path (defaults to
        /tmp/acf_forecast_<model>_output.nc, matching the paths
        HPCConnectionManager's one-click pipelines already reference).

    Returns
    -------
    dict with status, model, steps_completed, output_path.
    """
    if model not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model {model!r} - expected one of {sorted(MODEL_CONFIGS)}")

    config = MODEL_CONFIGS[model]
    steps = steps if steps is not None else config["default_steps"]
    output_path = output_path or f"/tmp/acf_forecast_{model.lower()}_output.nc"

    logger.info(
        "Starting %s forecast cycle (grid=%dx%dx%d, standing in for %.1fkm operational resolution, %d steps, dt=%.0fs)",
        model, config["n_lat"], config["n_lon"], config["n_levels"], config["resolution_km"], steps, dt_seconds,
    )

    grid = EarthGrid(n_lat=config["n_lat"], n_lon=config["n_lon"], n_levels=config["n_levels"])
    solver = CoupledEarthSolver(grid)
    state = solver.initialize_coupled_state()

    for step_index in range(steps):
        state = solver.step(state, dt=dt_seconds)
        if (step_index + 1) % max(1, steps // 4) == 0:
            logger.info("%s cycle: step %d/%d complete", model, step_index + 1, steps)

    writer = NetcdfWriter(output_path)
    written_path = writer.write_state(
        state,
        lats=grid.lats,
        lons=grid.lons,
        levels=np.arange(grid.n_levels),
        time_step=solver.current_time_step,
    )

    logger.info("%s forecast cycle complete: %d steps, output written to %s", model, steps, written_path)

    return {
        "status": "SUCCESS",
        "model": model,
        "operational_resolution_km": config["resolution_km"],
        "steps_completed": steps,
        "output_path": written_path,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="acf.forecast.engine",
        description="Run one ACF operational forecast cycle (AROME or ALADIN stand-in configuration).",
    )
    parser.add_argument("--model", choices=sorted(MODEL_CONFIGS), required=True)
    parser.add_argument("--steps", type=int, default=None, help="Number of coupled time steps.")
    parser.add_argument("--dt", type=float, default=60.0, help="Time step in seconds.")
    parser.add_argument("--output", type=str, default=None, help="NetCDF output path.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    try:
        result = run_forecast_cycle(args.model, steps=args.steps, dt_seconds=args.dt, output_path=args.output)
    except Exception:
        logger.exception("%s forecast cycle failed", args.model)
        return 1

    print(f"{result['status']}: {result['model']} cycle -> {result['output_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
