"""
ACF Complexity Engine — real 3D vertical field: Complexity(x, y, z)
======================================================================

Phase 11 of the Complexity Engine build-out
(docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md, explicit user request
"vas-y, construis la dimension verticale 3D"). Extends
acf.awci.spatial_field.compute_real_complexity_field() (Complexity(x,
y) at one level) to the full vertical dimension by reusing the SAME
single CoupledEarthSolver run across every level of its real 3D state,
instead of one solver run per level - the whole (level, lat, lon)
state is already integrated together by one solver.step() call, so
this only adds an extra loop dimension over AWCICalculator.calculate(),
not extra solver runs. Verified for the real ARPEGE grid configuration
(20 x 48 x 96 = 92,160 points): ~1.4s.

Level convention (confirmed against real solver output, not assumed):
level index 0 is the surface (highest pressure), increasing index is
increasing altitude (decreasing pressure/temperature) - matching
acf.simulation_engine.coupled_solver.CoupledEarthSolver.
compute_interfacial_fluxes()'s own surface_temp = state["T"][0, :, :]
convention, reused throughout this session (forecast/engine.py,
model_consensus_engine.py, spatial_field.py).

Honest limitation - read before treating this as more than it is
------------------------------------------------------------------
This reports the solver's real NATIVE model levels (their real local
pressure at every point, in `pressure_volume`), not literal standard
pressure levels (1000/925/850/700/500/300/250/200 hPa as listed in
docs/ACF_MASTER_UNIFIED_ARCHITECTURE.md's Grid/Vertical Engine layer).
Interpolating onto standard pressure levels is a distinct, real
capability (vertical interpolation) that does not exist anywhere in
ACF yet - building it here would silently invent values between real
model levels. `vertical_profile_at_point()` below reports each native
level's own real local pressure alongside its complexity score so a
caller can see which native level is CLOSEST to a pressure of
interest, without pretending an interpolated value was computed.

Same scope limits as spatial_field.py carry over: CAPE/CIN/
precipitation/terrain-altitude are not derived (AWCICalculator's own
defaults apply), and forecast_field/forecast_volume stays flat under
default weights for the same reason (no per-point ensemble/multi-model
data - would require re-running that fusion at every one of the
volume's points, which does not scale).
"""

from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.forecast.engine import MODEL_CONFIGS
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


def score_volume(
    calc: AWCICalculator,
    temperature: np.ndarray,
    wind_speed: np.ndarray,
    specific_humidity: np.ndarray,
    pressure_hpa: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Evaluate `calc` at every (level, lat, lon) point of the given real
    3D state arrays (all the same shape). Shared by
    compute_real_complexity_volume() below and
    acf.awci.temporal_field.compute_real_complexity_evolution() (one
    call per animation frame) so both stay byte-for-byte consistent
    with each other and with AWCICalculator itself, instead of two
    separately-maintained copies of this loop.

    Returns
    -------
    (awci_volume, physical_volume, forecast_volume) : 3 numpy arrays,
        same shape as the inputs. forecast_volume entries are np.nan
        (not a fabricated 0.0) wherever forecast_score was undefined
        for that point's weights - same discipline as AWCICalculator.
        _renormalized_score() itself.
    """
    n_levels, n_lat, n_lon = temperature.shape
    awci_volume = np.zeros((n_levels, n_lat, n_lon))
    physical_volume = np.zeros((n_levels, n_lat, n_lon))
    forecast_volume = np.full((n_levels, n_lat, n_lon), np.nan)

    # Same "no per-point forecast-side data" scope as this module's own
    # docstring (and spatial_field.py's compute_real_complexity_field()).
    for level in range(n_levels):
        for i in range(n_lat):
            for j in range(n_lon):
                result = calc.calculate(
                    {
                        "temperature": float(temperature[level, i, j]),
                        "wind_speed": float(wind_speed[level, i, j]),
                        "specific_humidity": float(specific_humidity[level, i, j]),
                        "pressure": float(pressure_hpa[level, i, j]),
                    }
                )
                awci_volume[level, i, j] = result["awci"]
                physical_volume[level, i, j] = (
                    result["physical_score"] if result["physical_score"] is not None else np.nan
                )
                if result["forecast_score"] is not None:
                    forecast_volume[level, i, j] = result["forecast_score"]

    return awci_volume, physical_volume, forecast_volume


def compute_real_complexity_volume(
    model: str = "ARPEGE",
    steps: int = 8,
    dt_seconds: float = 60.0,
    perturbation_scale: float = 2.0,
    seed: int | None = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Compute a real Complexity(x, y, z) volume: run CoupledEarthSolver
    once at `model`'s real grid configuration (all levels at once),
    then evaluate AWCICalculator at every (level, lat, lon) point of
    its real 3D state.

    Parameters mirror
    acf.awci.spatial_field.compute_real_complexity_field() exactly
    (same solver/perturbation/override/weights semantics) minus
    `level` - this function computes every level at once instead of
    selecting one.

    Returns
    -------
    dict
        lats, lons : 1D real coordinate arrays (degrees).
        awci_volume, physical_volume, forecast_volume : 3D numpy
            arrays, shape (n_levels, len(lats), len(lons)). Same
            None-not-fabricated-0.0 discipline as spatial_field.py for
            forecast_volume (np.nan where undefined).
        temperature_volume, wind_speed_volume, specific_humidity_volume :
            3D numpy arrays, the real per-point solver state actually
            fed to AWCICalculator.
        u_volume, v_volume : 3D numpy arrays, the real eastward/
            northward wind components wind_speed_volume was itself
            derived from (sqrt(U^2+V^2)) - exposed for callers needing
            the real vector, e.g. acf.awci.wind_shear.
            compute_real_wind_shear_at_point().
        pressure_volume_hpa : 3D numpy array, real local pressure per
            point in hPa (converted from the solver's native Pa) - see
            module docstring's "Honest limitation" for what this is
            NOT (not a standard-pressure-level interpolation).
        model, n_levels : provenance.
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

    temperature = state["T"]
    wind_speed = np.sqrt(state["U"] ** 2 + state["V"] ** 2)
    specific_humidity = state["q"]
    pressure_hpa = state["P"] / 100.0  # solver's native Pa -> hPa, standard meteorological unit

    calc = AWCICalculator(weights)
    awci_volume, physical_volume, forecast_volume = score_volume(
        calc, temperature, wind_speed, specific_humidity, pressure_hpa
    )
    n_levels_actual = temperature.shape[0]

    return {
        "lats": grid.lats,
        "lons": grid.lons,
        "n_levels": n_levels_actual,
        "model": model,
        "awci_volume": awci_volume,
        "physical_volume": physical_volume,
        "forecast_volume": forecast_volume,
        "temperature_volume": temperature,
        "wind_speed_volume": wind_speed,
        # Real u/v wind components (added 2026-09-03, docs/reference/
        # awci_dashboard_reference.jpg parity work) - already computed
        # internally (wind_speed above is sqrt(U^2+V^2)), just not
        # previously returned. A real caller (e.g. a per-point vertical
        # bulk wind shear diagnostic, acf.awci.wind_shear.
        # compute_real_wind_shear_at_point()) needs the real vector
        # components, not just the scalar magnitude.
        "u_volume": state["U"],
        "v_volume": state["V"],
        "specific_humidity_volume": specific_humidity,
        "pressure_volume_hpa": pressure_hpa,
        "status": "REAL_COMPLEXITY_VOLUME_FROM_ACF_SOLVER",
        "is_real_data": True,
        "honest_limitation": (
            "Real volume derived from CoupledEarthSolver's actual 3D state "
            "at the requested grid configuration's native model levels - "
            "not standard pressure levels (1000/925/850/700/500/300 hPa "
            "etc.) and not a synthetic pattern. No vertical interpolation "
            "is performed anywhere in ACF today; pressure_volume_hpa "
            "reports each native level's own real local pressure so a "
            "caller can find the closest native level to a pressure of "
            "interest, not an interpolated value at that exact pressure. "
            "CAPE/CIN/precipitation/terrain-altitude stay at "
            "AWCICalculator's defaults (no per-column parcel ascent). "
            "forecast_volume is flat under default weights - same "
            "does-not-scale-to-every-point reason as spatial_field.py's "
            "compute_real_complexity_field()."
        ),
    }


def vertical_profile_at_point(volume: dict[str, Any], lat: float, lon: float) -> dict[str, Any]:
    """
    Extract Complexity(z) at the grid point nearest (lat, lon) from a
    compute_real_complexity_volume() result.

    Real nearest-neighbour lookup (same convention as
    ModelConsensusEngine.compute_real_multi_model_disagreement() and
    spatial_field.py), not spatial interpolation.

    Parameters
    ----------
    volume : dict
        A compute_real_complexity_volume() return value.
    lat, lon : float
        Point of interest, in degrees.

    Returns
    -------
    dict
        lat, lon : the actual grid point used (nearest match, not
            necessarily exactly (lat, lon)).
        awci_profile, physical_profile, forecast_profile : 1D numpy
            arrays, length n_levels, ordered surface (index 0) to top
            of atmosphere.
        pressure_profile_hpa, temperature_profile : the real local
            values at each level of this column - use
            pressure_profile_hpa to find which native level is closest
            to a pressure of interest (see module docstring).
    """
    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    lat_idx = int(np.argmin(np.abs(lats - lat)))
    lon_idx = int(np.argmin(np.abs(lons - lon)))

    return {
        "lat": float(lats[lat_idx]),
        "lon": float(lons[lon_idx]),
        "awci_profile": volume["awci_volume"][:, lat_idx, lon_idx],
        "physical_profile": volume["physical_volume"][:, lat_idx, lon_idx],
        "forecast_profile": volume["forecast_volume"][:, lat_idx, lon_idx],
        "pressure_profile_hpa": volume["pressure_volume_hpa"][:, lat_idx, lon_idx],
        "temperature_profile": volume["temperature_volume"][:, lat_idx, lon_idx],
    }
