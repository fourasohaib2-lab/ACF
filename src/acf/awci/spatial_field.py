"""
ACF Complexity Engine — real 2D spatial field: Complexity(x, y)
=================================================================

Phase 12 of the Complexity Engine build-out
(docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md, explicit user request
"vas-y, construis la dimension spatiale 2D"). Until this module,
AWCICalculator only ever ran at one (lat, lon) point per call - this
module produces a genuine 2D field by running the real physics solver
once and evaluating AWCICalculator at every one of its real grid
points, not a synthetic pattern.

Relationship to gui/dashboard/awci_synthetic_field.py
-------------------------------------------------------
That module already builds a 2D AWCI grid (`awci_grid()`), but its
INPUT fields are hand-built analytic wave patterns - honestly disclosed
there as a GUI demo device, not observations or a live run (see its own
docstring). This module is the real counterpart: its inputs
(temperature, wind, humidity, pressure) come from actually running
`acf.simulation_engine.coupled_solver.CoupledEarthSolver` - the same
real solver `acf.forecast.engine.run_forecast_cycle()` and
`ModelConsensusEngine.compute_real_multi_model_disagreement()` already
use - at one of `acf.forecast.engine.MODEL_CONFIGS`'s real grid
resolutions. Both modules are legitimate and serve different purposes
(fast, reproducible, easily-art-directed demo map vs. a real
physics-derived field); this one is not a replacement for the other.

Honest limitation
------------------
CAPE/CIN/precipitation/terrain-altitude are NOT derived here - they
are left at AWCICalculator's own defaults (0.0 contribution), because
computing a real CAPE/CIN at every grid point would need a full
per-column parcel-ascent calculation this module does not perform.
Only the state variables CoupledEarthSolver's state dict directly
provides at the requested level - temperature (T), wind speed (from
U, V), specific humidity (q), pressure (P) - feed the real field.
Declaring a fabricated CAPE from these alone (e.g. a rule-of-thumb
formula) would be exactly the kind of invented number this project's
audits exist to remove; the field is real but partial, and is labelled
as such in its return value.
"""

from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.forecast.engine import MODEL_CONFIGS
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid

#: State variables this module actually feeds AWCICalculator from -
#: see this module's own "Honest limitation" docstring section for
#: what is deliberately left out and why.
_FIELDS_USED = ("temperature", "wind_speed", "specific_humidity", "pressure")


def compute_real_complexity_field(
    model: str = "ARPEGE",
    steps: int = 8,
    dt_seconds: float = 60.0,
    perturbation_scale: float = 2.0,
    seed: int | None = 0,
    level: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Compute a real Complexity(x, y) field: run CoupledEarthSolver once
    at `model`'s real grid configuration, then evaluate AWCICalculator
    at every one of its real grid points.

    Parameters
    ----------
    model : str
        One of acf.forecast.engine.MODEL_CONFIGS's keys ("AROME",
        "ALADIN", "ARPEGE"). Selects the default grid resolution
        (overridable below) - same real infrastructure the one-click
        HPC pipelines and the multi-model fusion use.
    steps, dt_seconds : real CoupledEarthSolver integration parameters.
    perturbation_scale : float
        Std dev of a genuine Gaussian initial-condition perturbation
        added to the temperature field before integration (same
        convention as acf.ai.simulation.fno_training's training data
        and ModelConsensusEngine.compute_real_multi_model_disagreement)
        - without it, the solver's default uniform initial state
        produces a flat, uninteresting field. Set to 0.0 to disable.
    seed : int or None
        Seed for the perturbation's RNG - None means "no perturbation
        and no RNG call at all" (deterministic, flat starting field).
    level : int
        Vertical level index (default 0 - surface, per
        CoupledEarthSolver.compute_interfacial_fluxes()'s own
        surface_temp = state["T"][0, :, :] convention).
    n_lat, n_lon, n_levels : int, optional
        Override `model`'s configured grid size (e.g. for a fast,
        coarse field in tests). Defaults to MODEL_CONFIGS[model]'s
        real values.
    weights : dict, optional
        Passed through to AWCICalculator - same custom-weights
        mechanism as everywhere else in this package.

    Returns
    -------
    dict
        lats, lons : 1D real coordinate arrays (degrees) from the
            solver's own EarthGrid - the field's true axes, not an
            assumed regular spacing.
        awci_field, physical_field, forecast_field : 2D numpy arrays,
            shape (len(lats), len(lons)) - field[i, j] is the real
            AWCICalculator score at (lats[i], lons[j]).
            forecast_field entries are np.nan (not 0.0 - see
            AWCICalculator._renormalized_score()'s own None-not-0.0
            discipline) wherever forecast_score was undefined for that
            point's weights.
        temperature_field, wind_speed_field, specific_humidity_field,
        pressure_field : the real per-point CoupledEarthSolver values
            actually fed to AWCICalculator to produce the above -
            returned for transparency/debugging and so a caller (or a
            test) can independently verify awci_field/physical_field/
            forecast_field without re-running the solver a second time
            (which would not reproduce bit-identically - see this
            module's tests and ModelConsensusEngine.
            compute_real_multi_model_disagreement()'s own note on why).
        model, level, fields_used : provenance.
        status, is_real_data, honest_limitation : see module docstring.
    """
    if model not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model {model!r} - expected one of {sorted(MODEL_CONFIGS)}")
    config = MODEL_CONFIGS[model]

    grid = EarthGrid(
        n_lat=n_lat if n_lat is not None else config["n_lat"],
        n_lon=n_lon if n_lon is not None else config["n_lon"],
        n_levels=n_levels if n_levels is not None else config["n_levels"],
    )
    solver = CoupledEarthSolver(grid)
    state = solver.initialize_coupled_state()

    if seed is not None and perturbation_scale > 0.0:
        rng = np.random.default_rng(seed=seed)
        state["T"] = state["T"] + rng.normal(loc=0.0, scale=perturbation_scale, size=state["T"].shape)

    for _ in range(steps):
        state = solver.step(state, dt=dt_seconds)

    temperature = state["T"][level, :, :]
    wind_speed = np.sqrt(state["U"][level, :, :] ** 2 + state["V"][level, :, :] ** 2)
    specific_humidity = state["q"][level, :, :]
    pressure = state["P"][level, :, :]

    n_lat_actual, n_lon_actual = temperature.shape
    calc = AWCICalculator(weights)

    awci_field = np.zeros((n_lat_actual, n_lon_actual))
    physical_field = np.zeros((n_lat_actual, n_lon_actual))
    forecast_field = np.full((n_lat_actual, n_lon_actual), np.nan)

    # NOTE on forecast_field: no ensemble_members / model_realizations /
    # confidence is supplied per point below - computing those per grid
    # cell would mean re-running the ensemble/multi-model-fusion solver
    # passes at every cell (each ModelConsensusEngine.
    # compute_real_multi_model_disagreement() call alone runs the solver
    # 2-3 times), which does not scale to a whole field with today's
    # infrastructure. With AWCICalculator's DEFAULT_WEIGHTS this makes
    # forecast_field come out flat at 0.0 everywhere (confidence
    # defaults to 100.0 -> "no evidence of disagreement", not "forecast
    # is certain everywhere" - see AWCICalculator's own default
    # convention) - a real, non-fabricated result, but not yet a useful
    # spatial forecast-complexity signal. See this module's own
    # docstring/honest_limitation.
    for i in range(n_lat_actual):
        for j in range(n_lon_actual):
            result = calc.calculate(
                {
                    "temperature": float(temperature[i, j]),
                    "wind_speed": float(wind_speed[i, j]),
                    "specific_humidity": float(specific_humidity[i, j]),
                    "pressure": float(pressure[i, j]),
                }
            )
            awci_field[i, j] = result["awci"]
            physical_field[i, j] = result["physical_score"] if result["physical_score"] is not None else np.nan
            if result["forecast_score"] is not None:
                forecast_field[i, j] = result["forecast_score"]

    return {
        "lats": grid.lats,
        "lons": grid.lons,
        "model": model,
        "level": level,
        "fields_used": _FIELDS_USED,
        "awci_field": awci_field,
        "physical_field": physical_field,
        "forecast_field": forecast_field,
        "temperature_field": temperature,
        "wind_speed_field": wind_speed,
        "specific_humidity_field": specific_humidity,
        "pressure_field": pressure,
        "status": "REAL_COMPLEXITY_FIELD_FROM_ACF_SOLVER",
        "is_real_data": True,
        "honest_limitation": (
            "Real field derived from CoupledEarthSolver's actual state "
            "(temperature, wind, humidity, pressure) at the requested grid "
            "configuration - not a synthetic demo pattern. CAPE/CIN/"
            "precipitation/terrain-altitude are NOT derived here (no "
            "per-column parcel ascent performed) and stay at "
            "AWCICalculator's own defaults - the field is real but "
            "partial, not a full operational complexity analysis. "
            "forecast_field in particular is flat/uniform under default "
            "weights: no per-point ensemble/multi-model data is computed "
            "(would require re-running the multi-model fusion solver "
            "passes at every grid cell - does not scale with today's "
            "infrastructure), so forecast_score everywhere falls back to "
            "AWCICalculator's 'no signal supplied' default, not a real "
            "spatial forecast-uncertainty measurement yet."
        ),
    }
