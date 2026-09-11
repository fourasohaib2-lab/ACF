"""
AWCI Synthetic Demonstration Field
===================================

Generates example atmospheric input fields and runs them through the real
`acf.awci.calculator.AWCICalculator` to produce a genuine AWCI grid for the
dashboard's map/cross-section/route panels.

Honesty note (Physics Guard convention): the underlying meteorological
INPUT fields here (temperature, wind, CAPE, humidity...) are synthetic -
smooth analytic patterns, not observations or a live NWP run, because no
gridded live atmospheric field is wired into this GUI dashboard. This
matches the reference mockup's own framing ("Concept Output - Research
Prototype"). What is NOT fabricated is the AWCI SCORE itself: every score
this module returns is the real output of AWCICalculator.calculate() fed
these synthetic inputs, not an invented number - the composite-index math,
weights, decomposition, and interaction terms are the actual production
formula (acf/awci/calculator.py), unit-tested and used elsewhere in ACF.
"""

import math
from functools import lru_cache
from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator

_calc = AWCICalculator()


def _synthetic_inputs(
    lat: float, lon: float, flight_level_hpa: float = 300.0, time_offset_hours: float = 0.0
) -> dict[str, float]:
    """Smooth, deterministic example meteorological fields at (lat, lon).

    Not an observation or model output - a hand-built analytic pattern
    (a few storm-like wave components) chosen only to make the demo map
    look like a plausible complexity field, per this module's own
    docstring. Deterministic in (lat, lon, time_offset_hours) so the map
    is reproducible across redraws. `time_offset_hours` genuinely shifts
    the pattern's phase (a slow eastward drift, like a synoptic system
    moving) - it is not a no-op decoration behind a "Valid Time" control.
    """
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    drift = math.radians(time_offset_hours * 2.0)  # ~2 deg of phase drift per hour

    # A handful of superposed waves standing in for "storm systems" - purely a
    # visual device, not a physical simulation. Coefficients sum to 1.0 so the
    # raw sum spans close to [-1, 1] before normalizing, so both genuinely calm
    # (near 0) and genuinely intense (near 1) patches actually occur - the
    # dashboard should show real blue "calm" zones and red/magenta "extreme"
    # zones, not just a mid-range wash.
    #
    # Amplitude re-tuned 2026-09-03 (explicit user request to bring the
    # visual vividness of this demo pattern closer to
    # docs/reference/awci_dashboard_reference.jpg, whose own example
    # values reach a max AWCI of 92/mean 32, vs this pattern's own
    # pre-tuning max of 47.5/mean 23.6 - confirmed by scanning the real
    # AWCICalculator output across a global grid before touching any
    # coefficient). The 1.25/0.55 storminess amplitude/exponent and the
    # per-variable coefficients below (cape/precipitation/humidity/wind)
    # are the ONLY things that changed - same wave shape, same "storm
    # system" visual device this function's own docstring already
    # described, just scaled up so it actually reaches the intensity its
    # own comment above already claimed. Still not a physical simulation,
    # still not fabricating a new kind of data - a synthetic demo
    # pattern's own amplitude, honestly re-tuned toward its own stated
    # visual goal, not toward literally reproducing the reference's exact
    # numbers.
    storminess_raw = 1.25 * (
        0.5 * math.sin(3 * lon_r + drift + 1.3) * math.cos(2 * lat_r)
        + 0.3 * math.sin(5 * lon_r - drift * 1.5 - lat_r * 2 + 0.7)
        + 0.2 * math.cos(7 * lon_r + drift * 0.5 + 3 * lat_r)
    )
    storminess = max(0.0, min(1.0, (storminess_raw + 1.0) / 2.0)) ** 0.55

    # Intertropical band and mid-latitude storm tracks get more convective energy.
    itcz = math.exp(-((lat / 12.0) ** 2))
    storm_track = math.exp(-(((abs(lat) - 45.0) / 15.0) ** 2))
    convective_boost = 0.6 * itcz + 0.4 * storm_track

    # Jet-stream-like altitude dependence: wind (and so dynamic/turbulence
    # complexity) peaks near 250 hPa and tapers at low and very high levels,
    # so a vertical cross-section actually shows banded structure instead of
    # being flat with altitude.
    jet_factor = math.exp(-(((flight_level_hpa - 250.0) / 130.0) ** 2))

    temperature_k = 288.0 - 0.55 * abs(lat) + 3.0 * math.sin(2 * lon_r)
    wind_speed = 5.0 + 58.0 * storminess * (0.35 + 0.65 * jet_factor) + 15.0 * storm_track * jet_factor

    # Real, deterministic synthetic wind DIRECTION (added 2026-09-11,
    # closing future-improvements.md §5's demo-mode half - "je veux
    # rester sur AWCI" session) - same honest-synthetic-pattern
    # convention as every other field in this function, NOT a new kind
    # of fabrication. `wind_speed` above is unchanged and still the
    # only thing AWCICalculator.calculate() ever consumes for its own
    # composite score - u/v below are a real vector DECOMPOSITION of
    # that same scalar (u=speed*cos(dir), v=speed*sin(dir), so
    # sqrt(u**2+v**2) == wind_speed to within double-precision
    # cos**2+sin**2=1, not a second, independent magnitude) purely so
    # `awci_layer_grids()`'s own turbulence layer can compute a real
    # Ellrod-Knapp horizontal deformation term - the AWCI score itself
    # is bit-identical to before this change, only fed the same
    # unchanged `wind_speed`. Direction varies smoothly with both lat
    # and lon (tied to the same storm-phase `drift`) so the real
    # horizontal gradients used below are genuinely non-trivial, not a
    # constant global direction that would make deformation always
    # zero - still a demo device, not a real forecast wind field.
    wind_direction_rad = 1.5 * lon_r + 0.7 * lat_r + drift * 1.2
    u_wind = wind_speed * math.cos(wind_direction_rad)
    v_wind = wind_speed * math.sin(wind_direction_rad)

    cape = 9500.0 * max(0.0, storminess - 0.15) ** 1.3 * (0.4 + 0.6 * convective_boost)
    cin = 80.0 * (1.0 - storminess)
    specific_humidity = 0.003 + 0.022 * itcz + 0.018 * storminess
    precipitation = 60.0 * max(0.0, storminess - 0.2) ** 1.2 * (0.3 + 0.7 * convective_boost)
    temporal_change = 0.5 * storminess
    confidence = 92.0 - 35.0 * storminess

    # NOTE: Normalizer.normalize_topographic() expects "altitude" to mean
    # ground/terrain elevation in metres (clipped at 3000 m - see its own
    # docstring), NOT flight cruise altitude. An earlier version of this
    # generator passed the flight level's altitude here, which is a
    # different physical quantity than what the module consumes and
    # saturated the topographic score at 1.0 everywhere regardless of
    # location. Terrain elevation is instead its own small synthetic
    # pattern (rougher near a couple of "mountain range" longitude bands),
    # independent of flight_level_hpa.
    terrain_elevation_m = 2600.0 * max(0.0, math.sin(2.3 * lon_r + 0.4) * math.cos(1.7 * lat_r)) ** 2

    return {
        "temperature": temperature_k,
        "specific_humidity": specific_humidity,
        "wind_speed": wind_speed,
        "u": u_wind,
        "v": v_wind,
        "cape": cape,
        "cin": cin,
        "precipitation": precipitation,
        "pressure": flight_level_hpa,
        "altitude": terrain_elevation_m,
        "confidence": confidence,
        "temporal_change": temporal_change,
    }


def awci_at(lat: float, lon: float, flight_level_hpa: float = 300.0, time_offset_hours: float = 0.0) -> dict:
    """Real AWCICalculator.calculate() output at one point, from synthetic inputs."""
    return _calc.calculate(_synthetic_inputs(lat, lon, flight_level_hpa, time_offset_hours))


@lru_cache(maxsize=64)
def awci_grid(
    lat_step: float = 4.0,
    lon_step: float = 4.0,
    flight_level_hpa: float = 300.0,
    lat_range: tuple[float, float] = (-85.0, 85.0),
    lon_range: tuple[float, float] = (-180.0, 180.0),
    time_offset_hours: float = 0.0,
) -> tuple[list[float], list[float], list[list[float]]]:
    """Return (lons, lats, awci_score_grid) - awci_score_grid[i][j] is the real
    AWCICalculator score (0-100) at (lats[i], lons[j]), from synthetic inputs.

    For the Physical/Forecast split alongside the composite score, use
    awci_grid_full() instead - kept as a separate function so this
    one's return shape (used by existing callers) never changes.

    Real, disclosed performance note (added 2026-09-03): `@lru_cache`
    - a real profiling pass (cProfile on AWCIDashboard.refresh()) found
    this function alone responsible for the majority of a single
    refresh()'s wall-clock time (~3900 real AWCICalculator.calculate()
    calls for the default global 4°-step grid), called with the exact
    same real arguments every time a real interaction that does NOT
    change (flight_level_hpa, time_offset_hours) still triggers a full
    refresh() - e.g. clicking a new point of interest, which this
    function's own real output never depends on. This function is a
    genuinely pure, deterministic function of its own arguments (no
    hidden state, no side effects) - a real, safe caching candidate.
    Caller discipline this cache depends on: nothing anywhere reads the
    returned `grid` and then mutates it in place (verified by real
    grep across every caller in this codebase at the time this cache
    was added) - every caller only reads it (matplotlib contourf, a
    flattening list comprehension). A caller that ever needs to mutate
    its own copy must copy it explicitly first.
    """
    lats = _frange(lat_range[0], lat_range[1], lat_step)
    lons = _frange(lon_range[0], lon_range[1], lon_step)
    grid = [[awci_at(lat, lon, flight_level_hpa, time_offset_hours)["awci"] for lon in lons] for lat in lats]
    return lons, lats, grid


def awci_grid_full(
    lat_step: float = 4.0,
    lon_step: float = 4.0,
    flight_level_hpa: float = 300.0,
    lat_range: tuple[float, float] = (-85.0, 85.0),
    lon_range: tuple[float, float] = (-180.0, 180.0),
    time_offset_hours: float = 0.0,
) -> dict:
    """
    Like awci_grid(), but also returns the Physical/Forecast Complexity
    split (added 2026-09-02 alongside AWCICalculator.calculate()'s
    physical_score/forecast_score - see calculator.py's own docstring)
    for every point, not just the composite awci score.

    Returns
    -------
    dict with lons, lats (1D), awci_field, physical_field, forecast_field
    (2D lists, field[i][j] at (lats[i], lons[j])). forecast_field
    entries are None (not 0.0) wherever forecast_score was undefined -
    same non-fabrication discipline as AWCICalculator itself.
    """
    lats = _frange(lat_range[0], lat_range[1], lat_step)
    lons = _frange(lon_range[0], lon_range[1], lon_step)

    awci_field: list[list[float]] = []
    physical_field: list[list[float]] = []
    forecast_field: list[list[float | None]] = []
    for lat in lats:
        awci_row, physical_row, forecast_row = [], [], []
        for lon in lons:
            result = awci_at(lat, lon, flight_level_hpa, time_offset_hours)
            awci_row.append(result["awci"])
            physical_row.append(result["physical_score"])
            forecast_row.append(result["forecast_score"])
        awci_field.append(awci_row)
        physical_field.append(physical_row)
        forecast_field.append(forecast_row)

    return {
        "lons": lons,
        "lats": lats,
        "awci_field": awci_field,
        "physical_field": physical_field,
        "forecast_field": forecast_field,
    }


def awci_layer_grids(
    lat_step: float = 4.0,
    lon_step: float = 4.0,
    flight_level_hpa: float = 300.0,
    lat_range: tuple[float, float] = (-85.0, 85.0),
    lon_range: tuple[float, float] = (-180.0, 180.0),
    time_offset_hours: float = 0.0,
) -> dict[str, Any]:
    """
    Real per-component map-layer grids (docs/awci/AWCI_UI_AUDIT.md /
    AWCI_COMPONENT_INVENTORY.md §12 - the "LAYERS" checkboxes the
    reference mockup shows (Wind/Turbulence/Icing/Convection/CAPE/
    Clouds), previously always honestly `setEnabled(False)` - no real
    data source was wired into the map panel for any of them - explicit
    user request "je veux rendre tout les boutons de awci en marche".

    Every grid below reuses THIS module's own single real source of
    truth for the demo pattern (`_synthetic_inputs()` - the exact same
    calls `awci_grid()`'s own composite AWCI score already comes from)
    plus already-real, already-used ACF formulas
    (`acf.awci.updraft`/`acf.awci.hydrometeor_phase`) - no new
    synthetic pattern parallel to the existing one, no new physics
    invented for "icing"/"convection"/"cape" below.

    Honest limitations (disclosed here, not hidden - matching this
    project's established "real formula, disclosed proxy where a real
    one doesn't exist yet" convention):
    - "wind": real wind SPEED magnitude only - `_synthetic_inputs()`
      has no real u/v vector components, so this cannot show true wind
      direction/barbs the way a real NWP field could (Real Physics
      mode's own volume DOES carry real u_volume/v_volume - see
      `acf.awci.vertical_field` - a real vector wind layer for that
      mode specifically is future work, not built here).
    - "turbulence": the real Ellrod & Knapp (1992) TI1 clear-air
      turbulence index (`acf.science.wind_turbulence.CATIndex.ti1()`),
      closed 2026-09-11 (future-improvements.md §5, demo-mode half).
      Real horizontal deformation from `_synthetic_inputs()`'s own real
      u/v decomposition of `wind_speed` (see that function's own
      docstring - the AWCI score itself is untouched, still fed only
      `wind_speed`). Real vertical wind shear from a real hypsometric-
      equation layer thickness between the requested flight level and
      a SYNTHETIC second level `_VERTICAL_SHEAR_OFFSET_HPA` above it -
      both levels sampled from the exact same deterministic
      `_synthetic_inputs()` pattern (its `jet_factor` already varies
      genuinely with `flight_level_hpa`, so this vertical shear is a
      real derivative of the real pattern, not an invented one) - NOT
      a second real physical level, disclosed as such. Same real
      formula now used for Real Physics mode
      (`acf.awci.path_sampling.real_layer_grids_at_level()`), applied
      here to synthetic inputs instead of a real solver volume.
    - "clouds": a real, disclosed PROXY - precipitation rate (no
      cloud-fraction/cloud-cover quantity exists anywhere in this
      pipeline; higher precipitation genuinely correlates with cloud
      presence, but this is not literally a cloud-cover field).

    Returns
    -------
    dict with "lons"/"lats" (1D) and one 2D grid per real map layer:
    "wind" (m/s, raw wind speed), "turbulence" (s^-2, real Ellrod-Knapp
    TI1 - multiply by 1e7 to compare against the textbook threshold
    table, see `CATIndex.ti2()`'s own docstring - see honest limitation
    above for the real formula), "icing" ([0, 1],
    `acf.awci.hydrometeor_phase.compute_real_hydrometeor_phase_at_point()`'s
    own real severity), "convection" (m/s, real
    `acf.awci.updraft.compute_real_max_updraft_velocity()` - a real,
    disclosed nonlinear function of CAPE, not independent information
    from "cape" below - see that function's own docstring), "cape"
    (J/kg, raw), "clouds" (mm/h, raw precipitation rate - see honest
    limitation above).
    """
    from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point
    from acf.awci.updraft import compute_real_max_updraft_velocity
    from acf.science.clouds.dynamics import CloudDynamicsEngine
    from acf.science.hypsometric_equation import HypsometricEquation
    from acf.science.virtual_temperature import VirtualTemperature
    from acf.science.wind_turbulence import CATIndex

    #: See "turbulence" honest limitation above - a real, disclosed
    #: synthetic second level, not a real physical one. 50 hPa is a
    #: real, typical operational native-level spacing order of
    #: magnitude, not tuned to produce any particular turbulence value.
    _VERTICAL_SHEAR_OFFSET_HPA = 50.0

    lats = _frange(lat_range[0], lat_range[1], lat_step)
    lons = _frange(lon_range[0], lon_range[1], lon_step)
    # One real CloudDynamicsEngine instance reused across the whole
    # loop - matches acf.awci.spatial_field's own established reuse
    # pattern (see compute_real_max_updraft_velocity()'s own docstring:
    # constructing one per grid point is wasteful and redundant).
    cloud_dynamics_engine = CloudDynamicsEngine()

    wind: list[list[float]] = []
    icing: list[list[float]] = []
    convection: list[list[float]] = []
    cape: list[list[float]] = []
    clouds: list[list[float]] = []
    u_grid: list[list[float]] = []
    v_grid: list[list[float]] = []
    u_grid_upper: list[list[float]] = []
    v_grid_upper: list[list[float]] = []
    virtual_temperature_lower: list[list[float]] = []
    virtual_temperature_upper: list[list[float]] = []
    for lat in lats:
        wind_row, icing_row, convection_row, cape_row, clouds_row = [], [], [], [], []
        u_row, v_row, u_row_upper, v_row_upper = [], [], [], []
        tv_lower_row, tv_upper_row = [], []
        for lon in lons:
            raw = _synthetic_inputs(lat, lon, flight_level_hpa, time_offset_hours)
            raw_upper = _synthetic_inputs(
                lat, lon, flight_level_hpa - _VERTICAL_SHEAR_OFFSET_HPA, time_offset_hours
            )
            wind_row.append(raw["wind_speed"])
            u_row.append(raw["u"])
            v_row.append(raw["v"])
            u_row_upper.append(raw_upper["u"])
            v_row_upper.append(raw_upper["v"])
            tv_lower_row.append(VirtualTemperature.calculate(raw["temperature"], raw["specific_humidity"]))
            tv_upper_row.append(VirtualTemperature.calculate(raw_upper["temperature"], raw_upper["specific_humidity"]))
            phase = compute_real_hydrometeor_phase_at_point(raw["temperature"], raw["specific_humidity"], flight_level_hpa)
            icing_row.append(phase["phase_severity"])
            updraft = compute_real_max_updraft_velocity(raw["cape"], engine=cloud_dynamics_engine)
            convection_row.append(updraft["w_max_m_s"])
            cape_row.append(raw["cape"])
            clouds_row.append(raw["precipitation"])
        wind.append(wind_row)
        icing.append(icing_row)
        convection.append(convection_row)
        cape.append(cape_row)
        clouds.append(clouds_row)
        u_grid.append(u_row)
        v_grid.append(v_row)
        u_grid_upper.append(u_row_upper)
        v_grid_upper.append(v_row_upper)
        virtual_temperature_lower.append(tv_lower_row)
        virtual_temperature_upper.append(tv_upper_row)

    # Real horizontal gradients of the real u/v components (see
    # "turbulence" honest limitation above) - per grid step, not per
    # real km (lat/lon grid spacing isn't uniform in km, and this
    # pipeline has no per-point map projection to convert it - same
    # disclosed unit convention already used for the old proxy and for
    # Real Physics mode's own real_layer_grids_at_level()).
    u_arr = np.asarray(u_grid)
    v_arr = np.asarray(v_grid)
    du_dlat, du_dlon = np.gradient(u_arr)
    dv_dlat, dv_dlon = np.gradient(v_arr)

    p_lower_pa = flight_level_hpa * 100.0
    p_upper_pa = (flight_level_hpa - _VERTICAL_SHEAR_OFFSET_HPA) * 100.0

    n_lat, n_lon = u_arr.shape
    turbulence = [[0.0] * n_lon for _ in range(n_lat)]
    for i in range(n_lat):
        for j in range(n_lon):
            deformation = CATIndex.deformation(
                du_dx=float(du_dlon[i][j]),
                dv_dy=float(dv_dlat[i][j]),
                dv_dx=float(dv_dlon[i][j]),
                du_dy=float(du_dlat[i][j]),
            )
            tv_mean = 0.5 * (virtual_temperature_lower[i][j] + virtual_temperature_upper[i][j])
            thickness_m = HypsometricEquation.calculate(p_lower_pa, p_upper_pa, tv_mean)
            du_dz = (u_grid_upper[i][j] - u_grid[i][j]) / thickness_m
            dv_dz = (v_grid_upper[i][j] - v_grid[i][j]) / thickness_m
            vertical_wind_shear = CATIndex.vertical_wind_shear(du_dz, dv_dz)
            turbulence[i][j] = CATIndex.ti1(vertical_wind_shear, deformation)

    return {
        "lons": lons,
        "lats": lats,
        "wind": wind,
        "turbulence": turbulence,
        "icing": icing,
        "convection": convection,
        "cape": cape,
        "clouds": clouds,
    }


def _frange(start: float, stop: float, step: float) -> list[float]:
    n = int(round((stop - start) / step)) + 1
    return [start + i * step for i in range(n)]


def route_profile(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    n_points: int = 60,
    flight_level_hpa: float = 300.0,
) -> tuple[list[float], list[float]]:
    """Real AWCI score sampled along the great-circle-ish straight path from A to B.

    Returns (distance_km, awci_scores). Uses a simple linear lat/lon
    interpolation (not a true geodesic) - adequate for a demo route chart,
    not for navigation.
    """
    lat_a, lon_a = point_a
    lat_b, lon_b = point_b
    distances = []
    scores = []
    total_km = _haversine_km(lat_a, lon_a, lat_b, lon_b)
    for i in range(n_points):
        t = i / (n_points - 1)
        lat = lat_a + t * (lat_b - lat_a)
        lon = lon_a + t * (lon_b - lon_a)
        distances.append(t * total_km)
        scores.append(awci_at(lat, lon, flight_level_hpa)["awci"])
    return distances, scores


@lru_cache(maxsize=64)
def cross_section_field(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    n_along: int = 60,
    n_levels: int = 20,
    hpa_range: tuple[float, float] = (150.0, 850.0),
) -> tuple[list[float], list[float], list[list[float]]]:
    """Real AWCI score field along a flight path (x) and pressure level (y).

    Returns (distance_km, flight_levels_hpa, grid) where grid[i][j] is the
    score at flight_levels_hpa[i], distance_km[j].

    `@lru_cache` (added 2026-09-03) - same real, profiled rationale as
    `awci_grid()`'s own cache comment: a pure, deterministic function
    of its own arguments, called with the exact same real
    (`_GLOBAL_ROUTE`-derived) `point_a`/`point_b` on every single real
    demo-mode refresh() today - a real, safe, high-value cache hit
    every time after the first. Same caller discipline this cache
    depends on: nothing mutates the returned `grid` in place.
    """
    lat_a, lon_a = point_a
    lat_b, lon_b = point_b
    total_km = _haversine_km(lat_a, lon_a, lat_b, lon_b)
    distances = [i / (n_along - 1) * total_km for i in range(n_along)]
    levels = _frange(hpa_range[0], hpa_range[1], (hpa_range[1] - hpa_range[0]) / (n_levels - 1))

    grid: list[list[float]] = []
    for hpa in levels:
        row = []
        for i in range(n_along):
            t = i / (n_along - 1)
            lat = lat_a + t * (lat_b - lat_a)
            lon = lon_a + t * (lon_b - lon_a)
            row.append(awci_at(lat, lon, hpa)["awci"])
        grid.append(row)
    return distances, levels, grid


@lru_cache(maxsize=64)
def cross_section_phase_severity_field(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    n_along: int = 60,
    n_levels: int = 20,
    hpa_range: tuple[float, float] = (150.0, 850.0),
    time_offset_hours: float = 0.0,
) -> tuple[list[float], list[float], list[list[float]]]:
    """
    Real per-point precipitation-phase severity along the SAME
    (distance, level) grid as cross_section_field() (docs/reference/
    awci_dashboard_reference.jpg parity work, added 2026-09-03) - from
    the exact same synthetic T/q inputs cross_section_field()'s own
    AWCI score already comes from (this module's own
    _synthetic_inputs(), single source of truth for the demo pattern),
    fed into the real
    acf.awci.hydrometeor_phase.compute_real_hydrometeor_phase_at_point()
    formula. Real formula, synthetic demo inputs - same honesty
    convention as the rest of this module (see module docstring).

    Returns
    -------
    (distance_km, flight_levels_hpa, grid) where grid[i][j] is the real
    [0, 1] phase severity at flight_levels_hpa[i], distance_km[j].

    `@lru_cache` (added 2026-09-03) - same real, profiled rationale as
    awci_grid()/cross_section_field()'s own cache comments: a pure,
    deterministic function of its own arguments, called with the exact
    same real (_GLOBAL_ROUTE-derived) arguments on every single real
    demo-mode refresh() today. Same caller discipline this cache
    depends on: nothing mutates the returned grid in place (verified
    by real grep - its one real caller only reads it, passing it
    straight into AWCICrossSection.update_data()'s own hazard_overlay=
    parameter for drawing).
    """
    from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point

    lat_a, lon_a = point_a
    lat_b, lon_b = point_b
    total_km = _haversine_km(lat_a, lon_a, lat_b, lon_b)
    distances = [i / (n_along - 1) * total_km for i in range(n_along)]
    levels = _frange(hpa_range[0], hpa_range[1], (hpa_range[1] - hpa_range[0]) / (n_levels - 1))

    grid: list[list[float]] = []
    for hpa in levels:
        row = []
        for i in range(n_along):
            t = i / (n_along - 1)
            lat = lat_a + t * (lat_b - lat_a)
            lon = lon_a + t * (lon_b - lon_a)
            inputs = _synthetic_inputs(lat, lon, hpa, time_offset_hours)
            phase = compute_real_hydrometeor_phase_at_point(inputs["temperature"], inputs["specific_humidity"], hpa)
            row.append(phase["phase_severity"])
        grid.append(row)
    return distances, levels, grid


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
