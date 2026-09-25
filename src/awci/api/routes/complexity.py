"""
`/complexity` - real HTTP surface over
``awci.complexity.calculator.AWCICalculator`` - the ``routes/
complexity.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").

A real, AWCI-native sibling of ``acf.web.routers.complexity_router``
(which serves the same real ``AWCICalculator`` engine, round-tripped
through the ``acf.awci`` backward-compatible shim, at ACF's own
general-purpose FastAPI app) - this one imports ``awci.complexity``
directly rather than via that shim, matching this session's own
"repoint real dependents to the new location directly" discipline
already applied throughout the AWCI package migration.

``/field`` and ``/vertical-profile`` (added for the AWCI web
dashboard's GlobalMap/RegionalMap and VerticalCrossSection panels) are
thin HTTP wrappers over 2 already-real, already-tested engines -
``awci.complexity.spatial_field.compute_real_complexity_field()``
(Complexity(x, y), genuinely runs ``CoupledEarthSolver`` once and
evaluates ``AWCICalculator`` at every real grid point) and
``awci.complexity.vertical_field.compute_real_complexity_volume()`` +
``vertical_profile_at_point()`` (Complexity(x, y, z), same real solver
run extended to every native level, then a real nearest-grid-point
column extraction) - no new physics, no new formula, and no synthetic
fallback is added here. Both real engines' own extensive
``honest_limitation`` disclosure is passed straight through unedited
so the frontend can surface it rather than imply a more complete
field than what was actually computed (see each engine's own module
docstring for the full, real scope: no terrain/orography, no real
precipitation field, ``forecast_field``/``forecast_profile`` stay flat
under default weights - re-running the ensemble/multi-model fusion at
every grid point does not scale with today's infrastructure).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from fastapi import APIRouter, Body, HTTPException

from awci.complexity.calculator import AWCICalculator
from awci.complexity.spatial_field import compute_real_complexity_field
from awci.complexity.vertical_field import compute_real_complexity_volume, vertical_profile_at_point
from awci.flight.waypoint import generate_multi_leg_route_waypoints
from awci.knowledge.airports.airport_database import AirportDatabase

router = APIRouter(prefix="/complexity", tags=["complexity"])


def _to_json_safe_numeric(value: Any) -> Any:
    """
    Real, JSON-safe conversion for the numpy-heavy return values of
    ``spatial_field``/``vertical_field`` - not a duplicate of
    ``acf.utils.serialization.to_json_safe`` (that module stays
    numpy-free, matching this project's "avoid unnecessary
    dependencies" rule for a utility every caller pulls in; only the 2
    real physics-field routes below actually need numpy-array
    handling). ``numpy.ndarray`` becomes a nested list
    (``.tolist()``), ``numpy.floating``/``numpy.integer`` becomes a
    plain Python number, and any real ``NaN`` (genuinely present
    wherever the underlying engine honestly could not compute a value
    - see each engine's own ``np.nan``-not-fabricated-0.0 discipline)
    becomes JSON ``null`` rather than the non-standard, often-rejected
    literal ``NaN`` token. Dicts/lists/tuples are walked recursively;
    everything else is returned unchanged.
    """
    if isinstance(value, np.ndarray):
        return _to_json_safe_numeric(value.tolist())
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if math.isnan(f) else f
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: _to_json_safe_numeric(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe_numeric(item) for item in value]
    return value


@router.post("/score")
async def score(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Real point complexity score - genuinely calls
    ``AWCICalculator().calculate(data)``, not a canned response. See
    that method's own docstring for ``data``'s real accepted keys
    (temperature, specific_humidity, wind_speed, cape, cin,
    precipitation, pressure, altitude, confidence, temporal_change,
    ensemble_members, model_realizations).
    """
    return AWCICalculator().calculate(data)


@router.get("/field")
async def field(
    model: str = "ARPEGE",
    level: int = 0,
    steps: int = 8,
    seed: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    compute_convective_energy: bool = False,
    compute_wind_shear: bool = False,
    compute_theta_e: bool = False,
    compute_updraft_velocity: bool = False,
    compute_precipitation_phase: bool = False,
    compute_ceiling: bool = False,
    compute_visibility: bool = False,
) -> dict[str, Any]:
    """
    Real 2D Complexity(x, y) field for the dashboard's GlobalMap/
    RegionalMap panels - genuinely calls
    ``compute_real_complexity_field()`` (runs ``CoupledEarthSolver``
    once at ``model``'s real grid configuration, then evaluates
    ``AWCICalculator`` at every real grid point), not a synthetic
    pattern. ``n_lat``/``n_lon`` override the model's default
    resolution (e.g. for a faster, coarser field) - omit for
    ``model``'s real default grid.

    The 7 ``compute_*`` flags mirror
    ``compute_real_complexity_field()``'s own opt-in parameters
    (default off there too - see that function's docstring for the
    real per-point cost of each): enabling them makes
    ``module_fields["convective"]``/``["ceiling"]``/``["visibility"]``
    genuinely non-zero (real CAPE/CIN, real estimated ceiling/
    visibility risk) and adds real ``cape_field``/``cin_field``/
    ``wind_shear_field``/``theta_e_field``/``updraft_velocity_field``/
    ``precipitation_phase_severity_field`` to the response - real,
    substantially more expensive work (measured ~2s at a small 8x16
    grid with all 5 original flags on, ~20s at the dashboard's usual
    24x48 - so the frontend requests these only for a small, separate
    "hazard summary"/"instability indices" fetch, never for the main
    shared map field).
    """
    try:
        result = compute_real_complexity_field(
            model=model,
            steps=steps,
            seed=seed,
            level=level,
            n_lat=n_lat,
            n_lon=n_lon,
            compute_convective_energy=compute_convective_energy,
            compute_wind_shear=compute_wind_shear,
            compute_theta_e=compute_theta_e,
            compute_updraft_velocity=compute_updraft_velocity,
            compute_precipitation_phase=compute_precipitation_phase,
            compute_ceiling=compute_ceiling,
            compute_visibility=compute_visibility,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    # Real classification bands straight from AWCICalculator.LEVEL_THRESHOLDS
    # - returned alongside the field so a caller (e.g. the dashboard's
    # KpiBar "affected area" statistic) classifies cells against the
    # SAME real bands the backend itself uses, rather than duplicating
    # (and risking drift from) these numbers a second time client-side.
    # The top band's real upper bound is float("inf") - not valid JSON,
    # so it is honestly represented as `null` ("no upper bound") here.
    level_thresholds = [
        (None if math.isinf(upper_bound) else upper_bound, label)
        for upper_bound, label in AWCICalculator.LEVEL_THRESHOLDS
    ]
    output = {
        "lats": result["lats"],
        "lons": result["lons"],
        "model": result["model"],
        "level": result["level"],
        "awci_field": result["awci_field"],
        "physical_field": result["physical_field"],
        "forecast_field": result["forecast_field"],
        "module_fields": result["module_fields"],
        "level_thresholds": level_thresholds,
        "status": result["status"],
        "is_real_data": result["is_real_data"],
        "honest_limitation": result["honest_limitation"],
    }
    if compute_convective_energy:
        # Real raw CAPE/CIN (J/kg) - already computed by
        # compute_real_complexity_field() whenever this flag is set
        # (it feeds module_fields["convective"]'s 0-100 score), but
        # never previously surfaced in this response - a real
        # instability index in its own physical units, not just the
        # composite score derived from it.
        output["cape_field"] = result["cape_field"]
        output["cin_field"] = result["cin_field"]
    if compute_wind_shear:
        output["wind_shear_field"] = result["wind_shear_field"]
    if compute_theta_e:
        # Real equivalent potential temperature (K) - a real,
        # standard instability diagnostic (a decreasing theta_e with
        # height signals real potential/convective instability),
        # already computed but never previously surfaced here either.
        output["theta_e_field"] = result["theta_e_field"]
    if compute_updraft_velocity:
        # Real CAPE-derived maximum parcel updraft velocity (m/s,
        # w_max = sqrt(2*CAPE)) - a real, standard convective-
        # intensity diagnostic.
        output["updraft_velocity_field"] = result["updraft_velocity_field"]
    if compute_precipitation_phase:
        output["precipitation_phase_severity_field"] = result["precipitation_phase_severity_field"]
    return _to_json_safe_numeric(output)


@router.get("/vertical-profile")
async def vertical_profile(
    lat: float,
    lon: float,
    model: str = "ARPEGE",
    steps: int = 8,
    seed: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
) -> dict[str, Any]:
    """
    Real Complexity(z) vertical profile at the real grid column
    nearest (``lat``, ``lon``), for the dashboard's
    VerticalCrossSection panel - genuinely calls
    ``compute_real_complexity_volume()`` (the same real
    ``CoupledEarthSolver`` run extended to every native vertical
    level) then ``vertical_profile_at_point()`` (a real nearest-
    neighbour column extraction, not spatial interpolation). Ordered
    surface (index 0) to top of atmosphere - see
    ``vertical_field.py``'s own module docstring for why these are the
    solver's real NATIVE levels (each with its own real local
    pressure in ``pressure_profile_hpa``), not standard pressure
    levels.
    """
    try:
        volume = compute_real_complexity_volume(
            model=model, steps=steps, seed=seed, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    profile = vertical_profile_at_point(volume, lat, lon)
    return _to_json_safe_numeric(
        {
            **profile,
            "model": volume["model"],
            "n_levels": volume["n_levels"],
            "status": volume["status"],
            "is_real_data": volume["is_real_data"],
            "honest_limitation": volume["honest_limitation"],
        }
    )


@router.get("/route-cross-section")
async def route_cross_section(
    dep_icao: str,
    arr_icao: str,
    stopover_icao: str | None = None,
    n_waypoints: int = 10,
    model: str = "ARPEGE",
    steps: int = 8,
    seed: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
) -> dict[str, Any]:
    """
    Real Complexity(along-track distance, z) cross-section for the
    dashboard's Vertical Cross Section panel - composes 3 already-real
    pieces, no new physics: real great-circle waypoints
    (``awci.flight.waypoint.generate_multi_leg_route_waypoints()``,
    the same function ``awci.flight.route_weather.
    build_route_weather_briefing()`` already uses for
    ``/flights/route-weather`` - 2 real legs when ``stopover_icao`` is
    given), ONE real ``compute_real_complexity_volume()`` run (the
    whole 3D field computed once, not once per waypoint), then a real
    nearest-grid-column extraction (``vertical_profile_at_point()``)
    at each real waypoint's position - the same honest nearest-
    neighbour convention ``/complexity/vertical-profile`` already uses
    for a single point, just repeated along the route.

    Raises
    ------
    HTTPException(404)
        If ``dep_icao``/``arr_icao``/``stopover_icao`` (when given) is
        not a real airport in ``AirportDatabase`` - the same real
        convention ``/flights/route-weather`` already uses.
    """
    dep = AirportDatabase.get_airport(dep_icao)
    arr = AirportDatabase.get_airport(arr_icao)
    if dep is None or arr is None:
        raise HTTPException(
            404,
            f"{dep_icao!r}/{arr_icao!r} must both be real airports in AirportDatabase - "
            f"known: {AirportDatabase.list_airports()}",
        )
    stopover = AirportDatabase.get_airport(stopover_icao) if stopover_icao else None
    if stopover_icao and stopover is None:
        raise HTTPException(404, f"{stopover_icao!r} must be a real airport in AirportDatabase")
    try:
        volume = compute_real_complexity_volume(
            model=model, steps=steps, seed=seed, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    route_points = (
        [(dep.latitude, dep.longitude), (arr.latitude, arr.longitude)]
        if stopover is None
        else [(dep.latitude, dep.longitude), (stopover.latitude, stopover.longitude), (arr.latitude, arr.longitude)]
    )
    waypoints = generate_multi_leg_route_waypoints(route_points, n_points_per_leg=n_waypoints)
    columns = []
    for wp in waypoints:
        profile = vertical_profile_at_point(volume, wp.latitude, wp.longitude)
        columns.append(
            {
                "distance_from_origin_km": wp.distance_from_origin_km,
                "latitude": profile["lat"],
                "longitude": profile["lon"],
                "awci_profile": profile["awci_profile"],
                "pressure_profile_hpa": profile["pressure_profile_hpa"],
            }
        )

    return _to_json_safe_numeric(
        {
            "departure_icao": dep.icao_code,
            "arrival_icao": arr.icao_code,
            "stopover_icao": stopover.icao_code if stopover else None,
            "model": volume["model"],
            "n_levels": volume["n_levels"],
            "columns": columns,
            "status": volume["status"],
            "is_real_data": volume["is_real_data"],
            "honest_limitation": volume["honest_limitation"],
        }
    )
