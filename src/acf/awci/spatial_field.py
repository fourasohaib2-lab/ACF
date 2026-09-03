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
Precipitation/terrain-altitude are still NOT derived here - CoupledEarthSolver's
state has no real precipitation field at all (see acf.events package
docstring's own confirmation), and no terrain/orography field. CAPE/CIN
WERE in this category until `compute_convective_energy=True` was added
(explicit user request, closing this exact limitation) - see that
parameter's own docstring and `acf.awci.convective_energy` for the real
per-column parcel-ascent calculation now available (opt-in, not the
default, because it is real, per-point extra work - a genuine
MetPy-based parcel ascent per grid cell, not free). With it left at the
default False, CAPE/CIN stay at AWCICalculator's own defaults (0.0
contribution) exactly as before - this module never silently changes
its own default output. Only the state variables CoupledEarthSolver's
state dict directly provides at the requested level - temperature (T),
wind speed (from U, V), specific humidity (q), pressure (P), plus the
real per-column CAPE/CIN when opted in - feed the real field. Declaring
a fabricated CAPE from a single level alone (e.g. a rule-of-thumb
formula) would be exactly the kind of invented number this project's
audits exist to remove; the field is real but partial, and is labelled
as such in its return value.
"""

from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point
from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.awci.updraft import compute_real_max_updraft_velocity
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.forecast.engine import MODEL_CONFIGS
from acf.science.clouds.dynamics import CloudDynamicsEngine
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid

#: State variables this module actually feeds AWCICalculator from -
#: see this module's own "Honest limitation" docstring section for
#: what is deliberately left out and why.
_FIELDS_USED = ("temperature", "wind_speed", "specific_humidity", "pressure")
#: Added when `compute_convective_energy=True` - see that parameter's
#: own docstring and `acf.awci.convective_energy`.
_CONVECTIVE_FIELDS_USED = ("cape", "cin")
#: Added when `compute_wind_shear=True` - see that parameter's own
#: docstring and `acf.awci.wind_shear`.
_WIND_SHEAR_FIELDS_USED = ("wind_shear",)
#: Added when `compute_theta_e=True` - see that parameter's own
#: docstring and `acf.awci.theta_e`.
_THETA_E_FIELDS_USED = ("theta_e",)
#: Added when `compute_updraft_velocity=True` - see that parameter's
#: own docstring and `acf.awci.updraft`.
_UPDRAFT_VELOCITY_FIELDS_USED = ("updraft_velocity",)
#: Added when `compute_precipitation_phase=True` - see that parameter's
#: own docstring and `acf.awci.hydrometeor_phase`.
_PRECIPITATION_PHASE_FIELDS_USED = ("precipitation_phase_severity",)


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
    compute_convective_energy: bool = False,
    compute_wind_shear: bool = False,
    compute_theta_e: bool = False,
    compute_updraft_velocity: bool = False,
    compute_precipitation_phase: bool = False,
    validate_physics: bool = False,
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
    compute_convective_energy : bool
        When True, genuinely computes real per-point CAPE/CIN (see
        `acf.awci.convective_energy.compute_real_cape_cin_at_point()`)
        from each grid point's real full vertical column and feeds
        them into AWCICalculator's convective module - closing this
        module's own former "CAPE/CIN NOT derived here" limitation
        (see module docstring). Off by default: a real MetPy parcel
        ascent per grid cell is genuine extra per-point cost this
        function's existing callers did not opt into, so the default
        output is unchanged unless explicitly requested.
    compute_wind_shear : bool
        When True, genuinely computes real per-point bulk wind shear
        (see `acf.awci.wind_shear.compute_real_wind_shear_at_point()`)
        between the surface (level 0) and the solver's own real
        highest native level, from each grid point's real full
        vertical U/V column, and feeds it into AWCICalculator's
        dynamic module (docs/ACF_MASTER_PROMPT.md section 12, explicit
        user request "commence par le module dynamique, avec le
        cisaillement de vent"). Off by default, same real-cost
        reasoning as `compute_convective_energy` - the default output
        is unchanged unless explicitly requested. See
        `acf.awci.wind_shear`'s own module docstring for why this real
        shear spans the full native-level column, not a fixed physical
        layer like 0-6 km.
    compute_theta_e : bool
        When True, genuinely computes real per-point equivalent
        potential temperature (theta-e, see
        `acf.awci.theta_e.compute_real_theta_e_at_point()` - the real,
        published Bolton (1980) formula) from each grid point's real
        temperature/specific humidity/pressure at `level`, and feeds
        it into AWCICalculator's thermodynamic module (docs/
        ACF_MASTER_PROMPT.md section 13, explicit user request
        "continue au module thermodynamique, avec theta-e"). Off by
        default - the default output is unchanged unless explicitly
        requested (a single-level computation, real but not free -
        3 real formula calls per grid point).
    compute_updraft_velocity : bool
        When True, genuinely computes real per-point maximum
        theoretical updraft velocity (see `acf.awci.updraft.
        compute_real_max_updraft_velocity()` - w_max = sqrt(2*CAPE),
        classic parcel theory) from each grid point's real CAPE, and
        feeds it into AWCICalculator's convective module (docs/
        ACF_MASTER_PROMPT.md section 14, explicit user request
        "continue au module convectif, avec le sommet des nuages" -
        see `acf.awci.updraft`'s own module docstring for why this is
        a real proxy for cloud-top development potential, not
        literally cloud top height, and why it is honestly disclosed
        as not independent information beyond CAPE itself). Requires
        `compute_convective_energy=True` (raises ValueError
        otherwise): this formula's only real input is CAPE, and reusing
        the SAME real per-point CAPE already computed for the
        convective module - rather than silently computing a second,
        possibly inconsistent one - keeps `data["cape"]` and
        `data["updraft_velocity"]` honestly derived from one real
        value. Off by default, same real-cost reasoning as the other
        `compute_*` flags above - the default output is unchanged
        unless explicitly requested. `updraft_velocity_field` stays
        `numpy.nan` (never a fabricated value) wherever the real
        per-point CAPE itself was not computed (too few real levels -
        see `acf.awci.convective_energy`'s own honest scope).
    compute_precipitation_phase : bool
        When True, genuinely computes real per-point surface
        precipitation-phase severity (see `acf.awci.hydrometeor_phase.
        compute_real_hydrometeor_phase_at_point()` - the real Stull
        (2011) wet-bulb formula composed with the real, self-disclosed
        `HydrometeorType.classify()` heuristic, then mapped to a real,
        disclosed ACF ordinal severity) from each grid point's real
        temperature/specific humidity/pressure at `level`, and feeds it
        into AWCICalculator's microphysical module (docs/
        ACF_MASTER_PROMPT.md section 15, candidate variable
        "hydrométéores"). Off by default - the default output is
        unchanged unless explicitly requested (a single-level
        computation, real but not free - 3 real formula calls per grid
        point, same cost class as `compute_theta_e`).
    validate_physics : bool
        When True, propagates a real, opt-in PhysicsGuard sanity check
        (docs/ACF_MASTER_PROMPT.md section 11) into every
        `compute_wind_shear`/`compute_theta_e`/`compute_precipitation_phase`
        sub-call that is itself enabled (see each of those real point
        modules' own `validate_physics` docstring - not
        `compute_updraft_velocity`, which has no documented CF
        operational range for CAPE to check against). Off by default,
        zero behavior change unless explicitly requested; raises a real
        `acf.core.exceptions.PhysicsError` immediately if the real
        solver's own state ever produces a genuinely out-of-range value
        at some grid point.

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
        module_fields : dict[str, 2D numpy array], docs/
            ACF_MASTER_PROMPT.md sections 28-29 ("Dynamic complexity,
            Thermodynamic complexity, Convective complexity, ..." as
            separate map layers) - one real 0-100 field per
            AWCICalculator module (dynamic/thermodynamic/convective/
            microphysical/topographic/temporal/confidence/
            ensemble_spread/model_disagreement - see
            AWCICalculator.PHYSICAL_MODULES/FORECAST_MODULES for the
            exact real set), each entry field[i, j] equal to
            `calculate(data_at_i_j)["module_scores"][name]` - the
            SAME per-point calculate() call awci_field/physical_field
            already come from, not a second pass.
        temperature_field, wind_speed_field, specific_humidity_field,
        pressure_field_hpa : the real per-point CoupledEarthSolver
            values actually fed to AWCICalculator to produce the above
            (pressure converted from the solver's native Pa to hPa) -
            returned for transparency/debugging and so a caller (or a
            test) can independently verify awci_field/physical_field/
            forecast_field without re-running the solver a second time
            (which would not reproduce bit-identically - see this
            module's tests and ModelConsensusEngine.
            compute_real_multi_model_disagreement()'s own note on why).
        cape_field, cin_field : 2D numpy arrays (J/kg), present only
            when `compute_convective_energy=True` - real per-point
            values from `acf.awci.convective_energy`, `numpy.nan`
            (never a fabricated 0.0) wherever fewer than 2 real levels
            remained above that module's own real pressure cutoff.
        wind_shear_field : 2D numpy array (m/s), present only when
            `compute_wind_shear=True` - real per-point bulk shear
            values from `acf.awci.wind_shear`, between the surface and
            the solver's own real highest native level (see that
            parameter's own docstring for why this is not a fixed
            physical layer).
        theta_e_field : 2D numpy array (K), present only when
            `compute_theta_e=True` - real per-point equivalent
            potential temperature from `acf.awci.theta_e`, `numpy.nan`
            (never a fabricated value) wherever the real computed
            relative humidity was non-positive at that point (see that
            module's own honest_limitation).
        updraft_velocity_field : 2D numpy array (m/s), present only
            when `compute_updraft_velocity=True` - real per-point
            maximum theoretical updraft velocity from
            `acf.awci.updraft`, derived from the SAME real per-point
            CAPE already in `cape_field`, `numpy.nan` (never a
            fabricated value) wherever that real CAPE was not computed.
        precipitation_phase_field : 2D numpy array (str dtype), and
            precipitation_phase_severity_field : 2D numpy array
            (float, [0, 1]) - present only when
            `compute_precipitation_phase=True` - real per-point surface
            precipitation phase and its ACF-assigned severity from
            `acf.awci.hydrometeor_phase` (see that module's own
            PHASE_SEVERITY for the real, disclosed ranking). Always
            real (never np.nan) - the underlying formula chain never
            fails to produce a phase, unlike theta_e/CAPE above.
        model, level, fields_used : provenance. fields_used includes
            "cape"/"cin" only when compute_convective_energy=True.
        status, is_real_data, honest_limitation : see module docstring.
    """
    if model not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model {model!r} - expected one of {sorted(MODEL_CONFIGS)}")
    if compute_updraft_velocity and not compute_convective_energy:
        raise ValueError(
            "compute_updraft_velocity=True requires compute_convective_energy=True - real "
            "maximum updraft velocity (acf.awci.updraft) is derived from real per-point CAPE, "
            "and reuses the SAME real CAPE already computed for the convective module rather "
            "than silently computing a second, possibly inconsistent one."
        )
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
    pressure_hpa = state["P"][level, :, :] / 100.0  # solver's native Pa -> hPa

    n_lat_actual, n_lon_actual = temperature.shape
    calc = AWCICalculator(weights)

    awci_field = np.zeros((n_lat_actual, n_lon_actual))
    physical_field = np.zeros((n_lat_actual, n_lon_actual))
    forecast_field = np.full((n_lat_actual, n_lon_actual), np.nan)
    # Real per-module 2D fields (docs/ACF_MASTER_PROMPT.md sections
    # 28-29 - "Dynamic complexity, Thermodynamic complexity, Convective
    # complexity, ..." as separate map layers, not just the combined
    # AWCI score). Zero extra solver/AWCICalculator cost: calculate()
    # already computes every module score at each point below - this
    # only keeps what the loop previously discarded. Module name set
    # comes from AWCICalculator's own PHYSICAL_MODULES/FORECAST_MODULES
    # union (the same real partition a dedicated test already enforces
    # covers every module calculate_module_scores() produces) - never
    # hardcoded separately here.
    module_names = sorted(calc.PHYSICAL_MODULES | calc.FORECAST_MODULES)
    module_fields: dict[str, np.ndarray] = {name: np.zeros((n_lat_actual, n_lon_actual)) for name in module_names}
    # np.nan (not 0.0) wherever compute_real_cape_cin_at_point() itself
    # honestly reports "not computed" - see its own None-not-0.0
    # discipline, mirrored here rather than silently defaulted.
    cape_field = np.full((n_lat_actual, n_lon_actual), np.nan) if compute_convective_energy else None
    cin_field = np.full((n_lat_actual, n_lon_actual), np.nan) if compute_convective_energy else None
    # Pa -> hPa for the full column, computed once outside the loop
    # (not per point) - only actually used when compute_convective_energy=True.
    pressure_hpa_column = state["P"] / 100.0
    # Real per-point bulk wind shear, only when compute_wind_shear=True
    # (docs/ACF_MASTER_PROMPT.md section 12 - see
    # acf.awci.wind_shear's own module docstring for the real formula
    # and its honest scope).
    wind_shear_field = np.zeros((n_lat_actual, n_lon_actual)) if compute_wind_shear else None
    # Real per-point equivalent potential temperature, only when
    # compute_theta_e=True (docs/ACF_MASTER_PROMPT.md section 13) -
    # np.nan (not a fabricated value) wherever
    # compute_real_theta_e_at_point() itself honestly reports
    # "not computed" (non-positive real relative humidity).
    theta_e_field = np.full((n_lat_actual, n_lon_actual), np.nan) if compute_theta_e else None
    # Real per-point maximum theoretical updraft velocity, only when
    # compute_updraft_velocity=True (docs/ACF_MASTER_PROMPT.md section
    # 14) - derived from the SAME real per-point CAPE already computed
    # above for cape_field, never a second/inconsistent one. np.nan
    # (not a fabricated value) wherever that real CAPE itself was not
    # computed. One CloudDynamicsEngine instance reused across the
    # whole loop (see acf.awci.updraft.compute_real_max_updraft_velocity's
    # own docstring for why constructing one per grid point would be
    # wasteful).
    updraft_velocity_field = np.full((n_lat_actual, n_lon_actual), np.nan) if compute_updraft_velocity else None
    cloud_dynamics_engine = CloudDynamicsEngine() if compute_updraft_velocity else None
    # Real per-point surface precipitation phase and its ACF-assigned
    # severity, only when compute_precipitation_phase=True (docs/
    # ACF_MASTER_PROMPT.md section 15) - always real (never np.nan),
    # the underlying formula chain (acf.awci.hydrometeor_phase) never
    # fails to produce a phase.
    precipitation_phase_field = (
        np.empty((n_lat_actual, n_lon_actual), dtype=object) if compute_precipitation_phase else None
    )
    precipitation_phase_severity_field = (
        np.zeros((n_lat_actual, n_lon_actual)) if compute_precipitation_phase else None
    )

    # NOTE (found while building this, not fixed here - out of scope):
    # AWCICalculator.calculate_module_scores() accepts a "pressure" key
    # in its input dict (documented in its own docstring, and
    # Normalizer.normalize_pressure() exists) but never actually reads
    # it anywhere in that method - it is currently a dead input.
    # Passing it below therefore has no effect on the scores computed;
    # it's still passed (and returned as pressure_field_hpa) because a
    # future AWCICalculator change might start using it, and because
    # the real local pressure is useful context on its own.
    #
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
            data: dict[str, Any] = {
                "temperature": float(temperature[i, j]),
                "wind_speed": float(wind_speed[i, j]),
                "specific_humidity": float(specific_humidity[i, j]),
                "pressure": float(pressure_hpa[i, j]),
            }

            if compute_convective_energy:
                # Real full vertical column at this one (i, j) point -
                # not a re-run of the solver, the same real state
                # already computed above just sliced differently.
                cape_cin = compute_real_cape_cin_at_point(
                    temperature_profile_k=state["T"][:, i, j],
                    specific_humidity_profile=state["q"][:, i, j],
                    pressure_profile_hpa=pressure_hpa_column[:, i, j],
                )
                if cape_cin["is_real_data"]:
                    data["cape"] = cape_cin["cape_j_kg"]
                    data["cin"] = cape_cin["cin_j_kg"]
                    assert cape_field is not None and cin_field is not None  # for mypy - both real when compute_convective_energy
                    cape_field[i, j] = cape_cin["cape_j_kg"]
                    cin_field[i, j] = cape_cin["cin_j_kg"]

                    if compute_updraft_velocity:
                        # Reuses this SAME real CAPE value - never a
                        # second, independently-computed one.
                        updraft = compute_real_max_updraft_velocity(
                            cape=cape_cin["cape_j_kg"], engine=cloud_dynamics_engine
                        )
                        data["updraft_velocity"] = updraft["w_max_m_s"]
                        assert updraft_velocity_field is not None  # for mypy - real whenever compute_updraft_velocity
                        updraft_velocity_field[i, j] = updraft["w_max_m_s"]
                # else: honestly leave data["cape"]/["cin"] unset (AWCICalculator's
                # own real defaults apply) and cape_field/cin_field stay np.nan -
                # never a fabricated 0.0 for a column with too few real levels.
                # updraft_velocity_field also stays np.nan here - no real CAPE
                # means no real updraft velocity either.

            if compute_wind_shear:
                # Real full vertical U/V column at this one (i, j)
                # point - same already-computed real state, sliced
                # differently, same discipline as compute_convective_energy above.
                shear = compute_real_wind_shear_at_point(
                    u_profile=state["U"][:, i, j],
                    v_profile=state["V"][:, i, j],
                    validate_physics=validate_physics,
                )
                data["wind_shear"] = shear["shear_m_s"]
                assert wind_shear_field is not None  # for mypy - real whenever compute_wind_shear
                wind_shear_field[i, j] = shear["shear_m_s"]

            if compute_theta_e:
                # Real single-level T/q/P at this point - already
                # available (temperature/specific_humidity/pressure_hpa
                # above), no extra column slicing needed.
                theta_e = compute_real_theta_e_at_point(
                    temperature_k=float(temperature[i, j]),
                    specific_humidity=float(specific_humidity[i, j]),
                    pressure_hpa=float(pressure_hpa[i, j]),
                    validate_physics=validate_physics,
                )
                assert theta_e_field is not None  # for mypy - real whenever compute_theta_e
                if theta_e["is_real_data"]:
                    data["theta_e"] = theta_e["theta_e_k"]
                    theta_e_field[i, j] = theta_e["theta_e_k"]
                # else: honestly leave data["theta_e"] unset (AWCICalculator's
                # own naive temperature/humidity blend applies) and
                # theta_e_field stays np.nan - never a fabricated value
                # for a point with non-positive real relative humidity.

            if compute_precipitation_phase:
                # Real single-level T/q/P at this point - same already-
                # available values as compute_theta_e above, no extra
                # column slicing needed.
                phase = compute_real_hydrometeor_phase_at_point(
                    temperature_k=float(temperature[i, j]),
                    specific_humidity=float(specific_humidity[i, j]),
                    pressure_hpa=float(pressure_hpa[i, j]),
                    validate_physics=validate_physics,
                )
                data["precipitation_phase_severity"] = phase["phase_severity"]
                assert precipitation_phase_field is not None  # for mypy
                assert precipitation_phase_severity_field is not None  # for mypy
                precipitation_phase_field[i, j] = phase["phase"]
                precipitation_phase_severity_field[i, j] = phase["phase_severity"]

            result = calc.calculate(data)
            awci_field[i, j] = result["awci"]
            physical_field[i, j] = result["physical_score"] if result["physical_score"] is not None else np.nan
            if result["forecast_score"] is not None:
                forecast_field[i, j] = result["forecast_score"]
            for name in module_names:
                module_fields[name][i, j] = result["module_scores"][name]

    fields_used: tuple[str, ...] = _FIELDS_USED
    if compute_convective_energy:
        fields_used = fields_used + _CONVECTIVE_FIELDS_USED
    if compute_wind_shear:
        fields_used = fields_used + _WIND_SHEAR_FIELDS_USED
    if compute_theta_e:
        fields_used = fields_used + _THETA_E_FIELDS_USED
    if compute_updraft_velocity:
        fields_used = fields_used + _UPDRAFT_VELOCITY_FIELDS_USED
    if compute_precipitation_phase:
        fields_used = fields_used + _PRECIPITATION_PHASE_FIELDS_USED

    output: dict[str, Any] = {
        "lats": grid.lats,
        "lons": grid.lons,
        "model": model,
        "level": level,
        "fields_used": fields_used,
        "awci_field": awci_field,
        "physical_field": physical_field,
        "forecast_field": forecast_field,
        "module_fields": module_fields,
        "temperature_field": temperature,
        "wind_speed_field": wind_speed,
        "specific_humidity_field": specific_humidity,
        "pressure_field_hpa": pressure_hpa,
        "status": "REAL_COMPLEXITY_FIELD_FROM_ACF_SOLVER",
        "is_real_data": True,
        "honest_limitation": (
            "Real field derived from CoupledEarthSolver's actual state "
            "(temperature, wind, humidity, pressure) at the requested grid "
            "configuration - not a synthetic demo pattern. "
            + (
                "Real per-point CAPE/CIN were also computed (compute_convective_energy=True) - "
                "see acf.awci.convective_energy for the real parcel-ascent method and its own "
                "honest scope (a documented 100 hPa cutoff, surface-based parcel only). "
                if compute_convective_energy
                else "CAPE/CIN stay at AWCICalculator's own defaults here "
                "(compute_convective_energy=False - see acf.awci.convective_energy for the real "
                "per-column parcel-ascent calculation available when it's requested). "
            )
            + "Precipitation/terrain-altitude are NOT derived here (no such field exists in "
            "CoupledEarthSolver's real state at all) - the field is real but partial, not a "
            "full operational complexity analysis. "
            "forecast_field in particular is flat/uniform under default "
            "weights: no per-point ensemble/multi-model data is computed "
            "(would require re-running the multi-model fusion solver "
            "passes at every grid cell - does not scale with today's "
            "infrastructure), so forecast_score everywhere falls back to "
            "AWCICalculator's 'no signal supplied' default, not a real "
            "spatial forecast-uncertainty measurement yet."
        ),
    }

    if compute_convective_energy:
        output["cape_field"] = cape_field
        output["cin_field"] = cin_field

    if compute_wind_shear:
        output["wind_shear_field"] = wind_shear_field

    if compute_theta_e:
        output["theta_e_field"] = theta_e_field

    if compute_updraft_velocity:
        output["updraft_velocity_field"] = updraft_velocity_field

    if compute_precipitation_phase:
        output["precipitation_phase_field"] = precipitation_phase_field
        output["precipitation_phase_severity_field"] = precipitation_phase_severity_field

    return output
