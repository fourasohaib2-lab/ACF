"""
ACF Complexity Engine — real 4D field: Complexity(x, y, z, t)
=================================================================

Phase 12 (final spatial phase) of the Complexity Engine build-out
(docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md, explicit user request
"vas-y, construis la dimension temporelle 4D"). Adds the time axis on
top of acf.awci.vertical_field.compute_real_complexity_volume()'s
Complexity(x, y, z): one CoupledEarthSolver instance is integrated
CONTINUOUSLY across the whole animation - each frame continues
forward from the previous frame's real physical state, not an
independent restarted run - and acf.awci.vertical_field.score_volume()
(the exact same helper compute_real_complexity_volume() uses) is
called once per frame, so a 4D result's frame 0 follows the exact same
code path compute_real_complexity_volume() alone would for the same
solver/perturbation/steps (see compute_real_complexity_evolution()'s
own docstring for why this is not the same as bit-identical output
across two separate calls).

Why continuous integration, not N independent runs
------------------------------------------------------
An earlier design considered re-running the solver from scratch for
each frame with steps=frame_index*steps_per_frame. That would still be
"real" in the sense that the solver genuinely runs, but each frame
would not be a continuation of the frame before it - i.e. not an
actual trajectory, more like N unrelated snapshots. Continuing the SAME
state object forward (this module's actual approach) makes
frame i+1 the real physical evolution of frame i under the solver's
own dynamics - the honest meaning of "4D": Complexity evolving through
real time, not independent complexity fields that happen to share a
config.

Honest limitation
-------------------
Same scope as vertical_field.py, carried through every frame:
CAPE/CIN/precipitation/terrain-altitude stay at AWCICalculator's
defaults, and forecast_evolution is flat under default weights for the
same does-not-scale-to-every-point-every-frame reason (real per-frame
ensemble/multi-model fusion would multiply an already-expensive
per-point cost by the number of frames). Performance: cost scales
linearly with n_frames (each frame pays vertical_field.py's own real
cost) - see this module's own compute_real_complexity_evolution()
docstring for measured timings.
"""

from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.awci.vertical_field import score_volume
from acf.forecast.engine import MODEL_CONFIGS
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


def compute_real_complexity_evolution(
    model: str = "ARPEGE",
    n_frames: int = 6,
    steps_per_frame: int = 4,
    dt_seconds: float = 60.0,
    perturbation_scale: float = 2.0,
    seed: int | None = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Compute a real Complexity(x, y, z, t) evolution: integrate
    CoupledEarthSolver continuously, taking a genuine snapshot every
    `steps_per_frame` steps and scoring the whole volume at each one
    (via acf.awci.vertical_field.score_volume()) - a real physical
    trajectory, not `n_frames` independent unrelated runs.

    Measured cost: linear in n_frames x vertical_field.py's own
    per-volume cost (~1.4s at full ARPEGE resolution, 20x48x96) - e.g.
    6 frames at full ARPEGE resolution is ~8-9s. Use the n_lat/n_lon/
    n_levels overrides for a fast field in tests/interactive use.

    Parameters
    ----------
    model, dt_seconds, perturbation_scale, seed, n_lat, n_lon,
    n_levels, weights : same real solver/perturbation/override/weights
        semantics as acf.awci.vertical_field.
        compute_real_complexity_volume() and
        acf.awci.spatial_field.compute_real_complexity_field().
    n_frames : int
        Number of snapshots to take (>= 1).
    steps_per_frame : int
        Real solver integration steps taken BETWEEN each snapshot
        (i.e. total steps by the end = n_frames * steps_per_frame).
        The perturbation (if any) is applied once, before frame 0's
        steps - not re-applied every frame, since that would be a
        fresh random kick at each frame rather than a single coherent
        trajectory's evolution.

    Returns
    -------
    dict
        lats, lons : 1D real coordinate arrays (degrees).
        n_levels, n_frames : provenance.
        valid_time_seconds : list[float], length n_frames - real
            cumulative simulated elapsed time at each snapshot
            ((frame_index + 1) * steps_per_frame * dt_seconds), i.e.
            frame 0 is captured AFTER its first steps_per_frame steps,
            not before any integration (there is no meaningful
            "before" complexity for an unperturbed, un-integrated
            state).
        awci_evolution, physical_evolution, forecast_evolution : 4D
            numpy arrays, shape (n_frames, n_levels, len(lats),
            len(lons)). Frame 0 uses the exact same code path as
            compute_real_complexity_volume(steps=steps_per_frame, ...)
            (same score_volume() helper, same solver call sequence) -
            but is NOT guaranteed bit-identical to a separate call to
            that function with the same arguments: CoupledEarthSolver's
            atmosphere/ocean components consume the global, unseeded
            np.random state internally (found earlier this session
            building ModelConsensusEngine.
            compute_real_multi_model_disagreement()), so two separate
            top-level calls in the same process can genuinely differ by
            a small amount depending on what else ran first.
        temperature_evolution, wind_speed_evolution,
        specific_humidity_evolution, pressure_evolution_hpa : 4D numpy
            arrays, same shape - the real per-frame state actually fed
            to AWCICalculator, returned for the same independent-
            verification reason as spatial_field.py/vertical_field.py.
        model : provenance.
        status, is_real_data, honest_limitation : see module docstring.
    """
    if n_frames < 1:
        raise ValueError("n_frames must be >= 1.")
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

    calc = AWCICalculator(weights)

    awci_frames = []
    physical_frames = []
    forecast_frames = []
    temperature_frames = []
    wind_speed_frames = []
    specific_humidity_frames = []
    pressure_frames = []
    valid_time_seconds = []

    for frame_index in range(n_frames):
        for _ in range(steps_per_frame):
            state = solver.step(state, dt=dt_seconds)

        temperature = state["T"]
        wind_speed = np.sqrt(state["U"] ** 2 + state["V"] ** 2)
        specific_humidity = state["q"]
        pressure_hpa = state["P"] / 100.0

        awci_volume, physical_volume, forecast_volume = score_volume(
            calc, temperature, wind_speed, specific_humidity, pressure_hpa
        )
        awci_frames.append(awci_volume)
        physical_frames.append(physical_volume)
        forecast_frames.append(forecast_volume)
        # Raw state per frame, kept for the same reason spatial_field.py
        # and vertical_field.py return their own raw fields: lets a
        # caller (or a test) independently verify a frame's complexity
        # fields without re-running the solver, which - see the note
        # above on bit-identical output - would not reproduce exactly.
        temperature_frames.append(temperature.copy())
        wind_speed_frames.append(wind_speed.copy())
        specific_humidity_frames.append(specific_humidity.copy())
        pressure_frames.append(pressure_hpa.copy())
        valid_time_seconds.append((frame_index + 1) * steps_per_frame * dt_seconds)

    return {
        "lats": grid.lats,
        "lons": grid.lons,
        "n_levels": grid.n_levels,
        "n_frames": n_frames,
        "valid_time_seconds": valid_time_seconds,
        "awci_evolution": np.stack(awci_frames, axis=0),
        "physical_evolution": np.stack(physical_frames, axis=0),
        "forecast_evolution": np.stack(forecast_frames, axis=0),
        "temperature_evolution": np.stack(temperature_frames, axis=0),
        "wind_speed_evolution": np.stack(wind_speed_frames, axis=0),
        "specific_humidity_evolution": np.stack(specific_humidity_frames, axis=0),
        "pressure_evolution_hpa": np.stack(pressure_frames, axis=0),
        "model": model,
        "status": "REAL_COMPLEXITY_EVOLUTION_FROM_ACF_SOLVER",
        "is_real_data": True,
        "honest_limitation": (
            "Real continuous trajectory (one CoupledEarthSolver instance "
            "integrated across all frames, each frame genuinely continuing "
            "the previous one's physical state), scored at every "
            "(frame, level, lat, lon) point via the same score_volume() "
            "helper compute_real_complexity_volume() uses - not a "
            "synthetic animation. Native model levels only (no standard-"
            "pressure-level interpolation - see vertical_field.py). "
            "CAPE/CIN/precipitation/terrain-altitude stay at "
            "AWCICalculator's defaults. forecast_evolution is flat under "
            "default weights at every frame - real per-frame ensemble/"
            "multi-model data would multiply an already-expensive "
            "per-point cost by n_frames, which does not scale with "
            "today's infrastructure."
        ),
    }


def profile_over_time(evolution: dict[str, Any], lat: float, lon: float, level: int = 0) -> dict[str, Any]:
    """
    Extract Complexity(t) at one (level, lat, lon) point across every
    frame of a compute_real_complexity_evolution() result - real
    nearest-neighbour lookup in space (same convention as
    vertical_field.py's vertical_profile_at_point()), exact index
    lookup in the vertical (no interpolation, as elsewhere).

    Parameters
    ----------
    evolution : dict
        A compute_real_complexity_evolution() return value.
    lat, lon : float
        Point of interest, in degrees.
    level : int
        Native model level index (default 0 - surface).

    Returns
    -------
    dict
        lat, lon, level : the actual point used.
        valid_time_seconds : the evolution's own time axis, unchanged.
        awci_series, physical_series, forecast_series : 1D numpy
            arrays, length n_frames.
    """
    if not (0 <= level < evolution["n_levels"]):
        raise ValueError(f"level {level} out of range [0, {evolution['n_levels']})")

    lats = np.asarray(evolution["lats"])
    lons = np.asarray(evolution["lons"])
    lat_idx = int(np.argmin(np.abs(lats - lat)))
    lon_idx = int(np.argmin(np.abs(lons - lon)))

    return {
        "lat": float(lats[lat_idx]),
        "lon": float(lons[lon_idx]),
        "level": level,
        "valid_time_seconds": evolution["valid_time_seconds"],
        "awci_series": evolution["awci_evolution"][:, level, lat_idx, lon_idx],
        "physical_series": evolution["physical_evolution"][:, level, lat_idx, lon_idx],
        "forecast_series": evolution["forecast_evolution"][:, level, lat_idx, lon_idx],
    }
