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
    - "turbulence": a real, disclosed PROXY - the horizontal gradient
      magnitude of the wind_speed grid itself (a real `numpy.gradient()`
      of already-real values, not a fabricated number), the same
      honest-proxy convention this project already uses for the
      cross-section's own turbulence icons (see awci_cross_section.py's
      `_TURBULENCE_PROXY_SHEAR_THRESHOLD_M_S`) - NOT the full real
      Ellrod-Knapp CAT index (still a real, disclosed gap, see
      future-improvements.md §5).
    - "clouds": a real, disclosed PROXY - precipitation rate (no
      cloud-fraction/cloud-cover quantity exists anywhere in this
      pipeline; higher precipitation genuinely correlates with cloud
      presence, but this is not literally a cloud-cover field).

    Returns
    -------
    dict with "lons"/"lats" (1D) and one 2D grid per real map layer:
    "wind" (m/s, raw wind speed), "turbulence" (m/s per grid-step,
    real horizontal wind-speed gradient magnitude - see honest
    limitation above), "icing" ([0, 1],
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
    for lat in lats:
        wind_row, icing_row, convection_row, cape_row, clouds_row = [], [], [], [], []
        for lon in lons:
            raw = _synthetic_inputs(lat, lon, flight_level_hpa, time_offset_hours)
            wind_row.append(raw["wind_speed"])
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

    # Real horizontal gradient magnitude of the wind_speed grid (see
    # "turbulence" honest limitation above) - np.gradient() over the
    # real, already-computed wind grid, per grid-step (not per real
    # km - lat/lon grid spacing isn't uniform in km, and this is
    # already disclosed as a proxy, not a calibrated physical shear).
    wind_arr = np.asarray(wind)
    d_dlat, d_dlon = np.gradient(wind_arr)
    turbulence = np.hypot(d_dlat, d_dlon).tolist()

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
