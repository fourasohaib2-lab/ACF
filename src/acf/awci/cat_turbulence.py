"""
ACF Complexity Engine — real Clear Air Turbulence index (Ellrod & Knapp
1992), cited by ICAO Doc 9837
=============================================================================

Explicit user request ("je veux que AWCI travaille avec les lois de
l'OACI et l'OMM"). Investigation found `acf.science.wind_turbulence.
CATIndex` - a real, complete implementation of the Ellrod & Knapp
(1992) Turbulence Index (TI1/TI2, also called EI - "Ellrod Index") -
already existed, already correctly implemented and unit-tested, but
was never called by anything in `acf.awci`: the map's own "Turbulence"
LAYERS checkbox used only a coarser proxy (the horizontal gradient
magnitude of wind SPEED alone), explicitly disclosed in that proxy's
own docstring as "NOT the full Ellrod-Knapp CAT index". Exactly the
same "real formula, never wired in" pattern this project's audits
exist to close - already found and fixed for CAPE/wind-shear/
microburst earlier in this same session.

`AVIATION_HAZARDS_REGISTRY["cat_turbulence"]` (acf.aviation.hazards.
aviation_hazards) already cites the real governing references for
this exact index: ICAO Doc 9837 "Manual on Low-level Wind Shear and
Turbulence", and Ellrod & Knapp (1992), Weather and Forecasting.

Real inputs composed, none invented
-------------------------------------
Every real quantity below is composed from already-real, already-
audited ACF functions - no new physics or formula invented here:

1. Real horizontal wind-component gradients (du/dx, du/dy, dv/dx,
   dv/dy, s^-1) - the same real local-Cartesian tangent-plane grid
   spacing (`acf.awci.workstation_fields.real_grid_spacing_m()`, dy =
   R*dphi, dx = R*cos(phi)*dlambda) that function's own
   `compute_real_vorticity_divergence()` already uses for real
   vorticity/divergence - reused here (imported directly, not
   reimplemented), just fed into `CATIndex.deformation()`/
   `.convergence()` instead of `VorticityCalculator`/`Divergence`.
2. Real vertical wind shear (du/dz, dv/dz, s^-1) between two real
   adjacent native levels - `acf.awci.wind_shear.
   compute_real_wind_shear_at_point()` already gives a real raw
   velocity difference (m/s) between two levels, but NOT divided by a
   real height difference (that function's own docstring already
   discloses ACF's native levels are not pinned to real physical
   heights) - genuinely dividing by height is required to get the
   real s^-1 unit `CATIndex.vertical_wind_shear()` expects (its own
   units are s^-1, matching the real Ellrod-Knapp formula's own
   dimensional requirement - TI1/TI2 are s^-2). The real height
   difference is estimated via `acf.science.encyclopedia.
   aerodynamics.isa_atmosphere.calculate_isa_pressure_altitude()`
   (built this same session, the exact analytic inverse of that
   module's own already-real, already-cited ISA pressure formula,
   ICAO Doc 7488) applied to each level's own real per-point pressure
   - honestly an ISA PRESSURE-altitude difference, not a true
   geopotential-height difference (same disclosure already established
   for that function).
3. `acf.science.wind_turbulence.CATIndex` itself - `vertical_wind_shear()`,
   `deformation()`, `convergence()`, `ti2()`, `category()` - called
   directly on the real per-point values above, never reimplemented.

Honest scope - what this is NOT
-----------------------------------
- TI2/EI (Ellrod's own empirical index, an operational CAT
  FORECASTING TECHNIQUE) is NOT the same quantity as the real EDR
  (Eddy Dissipation Rate) thresholds `AVIATION_HAZARDS_REGISTRY
  ["cat_turbulence"].icao_thresholds` also cites - both are real,
  both are cited by the same ICAO Doc 9837, but they are two DIFFERENT
  real metrics (EI is a diagnostic computed from analysis/forecast
  wind fields; EDR is derived from in-situ aircraft accelerometer
  measurements) - `category()`'s own real Ellrod-Knapp severity labels
  ("Smooth to Light"/"Light-Moderate"/"Moderate"/"Moderate-Severe")
  are reported here, never presented as an EDR value or compared
  numerically against the registry's own EDR thresholds.
- Only real in "Real Physics" mode: demo mode's own synthetic pattern
  (`acf.gui.dashboard.awci_synthetic_field._synthetic_inputs()`) has
  no real u/v vector decomposition, only a scalar wind speed - the
  deformation/convergence terms genuinely cannot be computed from that
  pattern without fabricating a wind direction. Demo mode keeps its
  own existing, already-disclosed wind-speed-gradient proxy unchanged.
- Real ISA pressure-altitude Δz, not a true geopotential-height Δz -
  see point 2 above and `calculate_isa_pressure_altitude()`'s own
  docstring for the disclosed real boundary-case tolerance.
- NaN (never a fabricated value), same real degenerate-case discipline
  already established in `workstation_fields.py`:
  a) at the pole rows (where real zonal grid spacing genuinely
     collapses to zero, same <1m physical threshold that module
     already uses),
  b) wherever the real ISA-pressure-altitude difference between the
     two levels used is too small to divide by safely (<1m, the same
     kind of real physical epsilon as (a), not an arbitrary tolerance),
  c) wherever the volume has only 1 real native level (no adjacent
     level exists at all to form a real vertical shear from).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.awci.workstation_fields import real_grid_spacing_m
from acf.aviation.hazards.aviation_hazards import AviationHazardEngine, AviationHazardInfo
from acf.science.encyclopedia.aerodynamics.isa_atmosphere import calculate_isa_pressure_altitude
from acf.science.wind_turbulence import CATIndex

#: Same real physical threshold `workstation_fields.
#: compute_real_vorticity_divergence()` already uses for the pole-row
#: degenerate-dx case - <1m of real zonal spacing is the pole itself
#: on any Earth-radius grid, not an arbitrary tolerance.
_DEGENERATE_DISTANCE_M = 1.0


def get_cat_turbulence_hazard_reference() -> AviationHazardInfo | None:
    """
    Real, full reference entry this module's index is grounded in -
    `acf.aviation.hazards.aviation_hazards.AVIATION_HAZARDS_REGISTRY
    ["cat_turbulence"]` (physical explanation, governing Richardson-
    number equation, real ICAO EDR thresholds, operational impacts,
    flight recommendations, references - ICAO Doc 9837, Ellrod & Knapp
    1992), exposed here so a caller (or a future GUI detail panel) can
    connect `compute_real_cat_index_at_level()`'s real per-point EI
    value back to the real encyclopedia entry it is grounded in - same
    real traceability pattern already established by
    `acf.awci.microburst.get_microburst_hazard_reference()`.
    """
    return AviationHazardEngine.get_hazard("cat_turbulence")


def compute_real_cat_index_at_level(volume: dict[str, Any], level_idx: int) -> dict[str, Any]:
    """
    Real per-point Ellrod & Knapp (1992) Turbulence Index (TI2/EI) at
    one real native level of a `compute_real_complexity_volume()`
    result, using the real adjacent level (`level_idx + 1`, or
    `level_idx - 1` if `level_idx` is already the top level) for the
    real vertical-shear term - see module docstring for the full
    real-composition disclosure and honest scope.

    Parameters
    ----------
    volume : a real `acf.awci.vertical_field.compute_real_complexity_volume()`
        result - needs its real "u_volume"/"v_volume"/
        "pressure_volume_hpa" (n_levels, n_lat, n_lon) and "lats"/"lons".
    level_idx : the real native level index to evaluate the index at.

    Returns
    -------
    dict
        ei_field : 2D real numpy array (n_lat, n_lon), raw s^-2 (the
            real Ellrod TI2 value - multiply by 1e7 to compare against
            the textbook 4/8/12 threshold table, same convention as
            `CATIndex.category()`'s own docstring). `nan` (never a
            fabricated value) at pole rows, wherever the real
            ISA-pressure-altitude level separation was too small to
            divide by safely, or wherever there is no real adjacent
            level at all.
        category_field : 2D numpy array of Python `str`, `CATIndex.
            category()`'s own real Ellrod-Knapp severity label per
            point, or `"UNDEFINED"` wherever `ei_field` is `nan`.
        vws_field, def_field, cvg_field : the real intermediate [s^-1]
            fields actually composed into `ei_field`, for transparency/
            debugging - same convention as `acf.awci.microburst`'s own
            intermediate signals.
        adjacent_level_idx : the real second level index actually used
            for the vertical-shear term (`None` if no adjacent level
            existed).
        status, is_real_data, honest_limitation.
    """
    u_volume = np.asarray(volume["u_volume"])
    v_volume = np.asarray(volume["v_volume"])
    pressure_hpa_volume = np.asarray(volume["pressure_volume_hpa"])
    lats = volume["lats"]
    lons = volume["lons"]
    n_levels, n_lat, n_lon = u_volume.shape

    if n_levels < 2:
        nan_field = np.full((n_lat, n_lon), np.nan)
        return {
            "ei_field": nan_field,
            "category_field": np.full((n_lat, n_lon), "UNDEFINED", dtype=object),
            "vws_field": nan_field.copy(),
            "def_field": nan_field.copy(),
            "cvg_field": nan_field.copy(),
            "adjacent_level_idx": None,
            "status": "CAT_INDEX_NOT_COMPUTED_NO_ADJACENT_LEVEL",
            "is_real_data": False,
            "honest_limitation": (
                "This real volume has only 1 native level - the real Ellrod-Knapp vertical-shear "
                "term needs 2 real adjacent levels, never fabricated from a single one."
            ),
        }

    adjacent_level_idx = level_idx + 1 if level_idx + 1 < n_levels else level_idx - 1
    bottom_idx, top_idx = sorted((level_idx, adjacent_level_idx))

    u_bottom = u_volume[bottom_idx]
    v_bottom = v_volume[bottom_idx]
    u_top = u_volume[top_idx]
    v_top = v_volume[top_idx]

    # Real horizontal gradients (s^-1) - same real local-Cartesian
    # tangent-plane grid spacing/pole-degeneracy discipline as
    # workstation_fields.compute_real_vorticity_divergence() (see
    # module docstring point 1) - evaluated at `level_idx` itself.
    u_here = u_volume[level_idx]
    v_here = v_volume[level_idx]
    dy, dx_per_row = real_grid_spacing_m(lats, lons)
    degenerate_dx = np.abs(dx_per_row) < _DEGENERATE_DISTANCE_M
    with np.errstate(divide="ignore", invalid="ignore"):
        du_dy = np.gradient(u_here, axis=0) / dy
        dv_dy = np.gradient(v_here, axis=0) / dy
        safe_dx_per_row = np.where(degenerate_dx, np.nan, dx_per_row)
        du_dx = np.gradient(u_here, axis=1) / safe_dx_per_row[:, None]
        dv_dx = np.gradient(v_here, axis=1) / safe_dx_per_row[:, None]

    # Real vertical shear (s^-1) - real ISA-pressure-altitude Δz
    # between the 2 real levels used (see module docstring point 2).
    altitude_bottom = np.vectorize(calculate_isa_pressure_altitude)(pressure_hpa_volume[bottom_idx] * 100.0)
    altitude_top = np.vectorize(calculate_isa_pressure_altitude)(pressure_hpa_volume[top_idx] * 100.0)
    delta_z = altitude_top - altitude_bottom
    degenerate_dz = np.abs(delta_z) < _DEGENERATE_DISTANCE_M
    with np.errstate(divide="ignore", invalid="ignore"):
        safe_delta_z = np.where(degenerate_dz, np.nan, delta_z)
        du_dz = (u_top - u_bottom) / safe_delta_z
        dv_dz = (v_top - v_bottom) / safe_delta_z

    ei_field = np.full((n_lat, n_lon), np.nan)
    vws_field = np.full((n_lat, n_lon), np.nan)
    def_field = np.full((n_lat, n_lon), np.nan)
    cvg_field = np.full((n_lat, n_lon), np.nan)
    category_field = np.full((n_lat, n_lon), "UNDEFINED", dtype=object)

    for i in range(n_lat):
        for j in range(n_lon):
            if not (
                np.isfinite(du_dx[i, j])
                and np.isfinite(du_dy[i, j])
                and np.isfinite(dv_dx[i, j])
                and np.isfinite(dv_dy[i, j])
                and np.isfinite(du_dz[i, j])
                and np.isfinite(dv_dz[i, j])
            ):
                continue  # honestly leave NaN/"UNDEFINED" - a real degenerate point (pole or zero Δz)
            vws = CATIndex.vertical_wind_shear(float(du_dz[i, j]), float(dv_dz[i, j]))
            deformation = CATIndex.deformation(
                float(du_dx[i, j]), float(dv_dy[i, j]), float(dv_dx[i, j]), float(du_dy[i, j])
            )
            convergence = CATIndex.convergence(float(du_dx[i, j]), float(dv_dy[i, j]))
            ei = CATIndex.ti2(vws, deformation, convergence)
            vws_field[i, j] = vws
            def_field[i, j] = deformation
            cvg_field[i, j] = convergence
            ei_field[i, j] = ei
            category_field[i, j] = CATIndex.category(ei)

    return {
        "ei_field": ei_field,
        "category_field": category_field,
        "vws_field": vws_field,
        "def_field": def_field,
        "cvg_field": cvg_field,
        "adjacent_level_idx": adjacent_level_idx,
        "status": "REAL_ELLROD_KNAPP_CAT_INDEX",
        "is_real_data": True,
        "honest_limitation": (
            "Real Ellrod & Knapp (1992) TI2/EI operational turbulence-forecasting index (ICAO Doc 9837) "
            "- NOT a true EDR (Eddy Dissipation Rate) measurement (a different real metric, derived from "
            "in-situ accelerometer data, also cited by the same ICAO document). Real ISA-pressure-altitude "
            "Δz between 2 native levels, not a true geopotential-height Δz."
        ),
    }
