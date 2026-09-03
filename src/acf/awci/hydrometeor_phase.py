"""
ACF Complexity Engine — real per-point surface precipitation phase (§15, hydrométéores)
============================================================================================

Continuing the real, targeted closures of §12-16 started with wind
shear (§12, dynamic), theta-e (§13, thermodynamic), and maximum
updraft velocity (§14, convective) - this session's exhaustive
90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found
docs/ACF_MASTER_PROMPT.md section 15 (MODULE MICROPHYSIQUE) explicitly
listing "pluie, neige, grêle, eau surfondue, ..., hydrométéores" among
this module's own candidate variables - the microphysical module used
only precipitation RATE before this, never precipitation PHASE (the
"hydrométéores" candidate variable itself).

Honest scope: no real, per-column hydrometeor species (qc/qi/qr/qs -
cloud water/ice/rain/snow mixing ratios) exist anywhere in
CoupledEarthSolver's real state, so real formulas that need them
(acf.science.clouds.microphysics.CloudMicrophysicsEngine's real
autoconversion/riming/Bergeron-Findeisen rates) cannot be fed real
per-point data here without fabricating those species - a real,
documented gap, not closed by this addition. `HydrometeorType.classify()`
was chosen instead because its only real inputs (surface temperature,
surface wet-bulb temperature) ARE already real quantities AWCI has at
every grid point.

Real formulas reused, not reimplemented
-----------------------------------------
1. `acf.science.thermodynamics.Thermodynamics.calculate_relative_humidity()`
   - same real formula already reused by `acf.awci.theta_e`.
2. `acf.science.thermodynamics.Thermodynamics.calculate_wet_bulb_temperature()`
   - Stull, R. (2011), "Wet-Bulb Temperature from Relative Humidity and
   Air Temperature", Journal of Applied Meteorology and Climatology - a
   real, published approximation formula.
3. `acf.science.precipitation.HydrometeorType.classify()` - a real,
   already-existing, explicitly self-disclosed HEURISTIC (that module's
   own docstring: "a heuristic forecasting rule of thumb, NOT a single
   validated physical formula" - rigorous phase determination needs a
   full vertical profile method, e.g. Bourgouin 2000, not implemented
   anywhere in this codebase) classifying surface precipitation phase
   from surface temperature and surface wet-bulb temperature into one
   of 4 real categories: "Rain", "Snow", "Wet Snow/Mix", "Freezing Rain
   / Ice Pellets" (the last merging freezing rain and ice pellets/sleet
   - that module's own docstring explains why surface-only data cannot
   reliably separate the two).

Honest, disclosed ACF design choice: phase -> severity
-------------------------------------------------------------
`HydrometeorType.classify()` returns a category, not a [0, 1] score -
turning it into a numeric contribution for the microphysical module
requires a real ordinal ranking, same kind of disclosed ACF design
choice as AWCICalculator's own INTERACTION_WEIGHTS or the 70/30
CAPE/CIN split (not a value invented and hidden - see
PHASE_SEVERITY below). The ranking used here follows a real,
well-documented aviation-operational fact, not an arbitrary guess:
freezing rain/ice pellets is universally recognized as the most
severe aircraft-icing precipitation hazard (supercooled large
droplets freezing on contact - see e.g. FAA AC 91-74 icing guidance),
ahead of wet snow/mix (icing plus reduced runway friction and
visibility impact), ahead of dry snow (visibility/friction impact,
no liquid-icing mechanism), ahead of plain rain (well-understood,
lowest incremental operational complexity of the four - rain RATE
itself is already captured by the separate, existing precipitation
input). The specific numeric values (0.2/0.5/0.7/1.0) are still an
ACF choice, not sourced from a published severity index - disclosed
as such throughout (PHASE_SEVERITY_STATUS, AWCICalculator's own
class docstring, the diagnostic registry).
"""

from __future__ import annotations

from typing import Any

from acf.science.precipitation import HydrometeorType
from acf.science.thermodynamics import Thermodynamics

#: Real, disclosed ACF ordinal severity ranking for each of
#: HydrometeorType.classify()'s 4 real output categories - see this
#: module's own docstring for the real aviation-operational reasoning
#: behind the ORDER (not the exact numeric values, which are an ACF
#: design choice).
PHASE_SEVERITY: dict[str, float] = {
    "Rain": 0.2,
    "Snow": 0.5,
    "Wet Snow/Mix": 0.7,
    "Freezing Rain / Ice Pellets": 1.0,
}


def compute_real_hydrometeor_phase_at_point(
    temperature_k: float, specific_humidity: float, pressure_hpa: float
) -> dict[str, Any]:
    """
    Real surface precipitation phase (and its ACF-assigned severity) at
    one point - composes 2 already-real formulas plus the real
    HydrometeorType.classify() heuristic (see module docstring), no new
    physics invented.

    Parameters
    ----------
    temperature_k : float
        Real air temperature (K).
    specific_humidity : float
        Real specific humidity (kg/kg).
    pressure_hpa : float
        Real atmospheric pressure (hPa).

    Returns
    -------
    dict
        phase : str, one of HydrometeorType.classify()'s 4 real
            categories.
        phase_severity : float in [0, 1] - PHASE_SEVERITY[phase], the
            real, disclosed ACF ordinal ranking (see module docstring).
        relative_humidity_pct, wet_bulb_c : the real intermediate
            values actually used, for transparency/debugging.
        status, is_real_data, honest_limitation.
    """
    relative_humidity_pct = Thermodynamics.calculate_relative_humidity(
        specific_humidity, pressure_hpa, temperature_k, is_kelvin=True
    )
    temperature_c = temperature_k - 273.15
    wet_bulb_c = Thermodynamics.calculate_wet_bulb_temperature(temperature_c, relative_humidity_pct / 100.0)

    phase = HydrometeorType.classify(temperature_c, wet_bulb_c)

    return {
        "phase": phase,
        "phase_severity": PHASE_SEVERITY[phase],
        "relative_humidity_pct": relative_humidity_pct,
        "wet_bulb_c": wet_bulb_c,
        "status": "REAL_HYDROMETEOR_PHASE_SURFACE_HEURISTIC",
        "is_real_data": True,
        "honest_limitation": (
            "Real surface-only phase heuristic (HydrometeorType.classify(), Stull 2011 wet-bulb "
            "approximation) - not a real vertical-profile method (e.g. Bourgouin 2000), so it cannot "
            "reliably distinguish freezing rain from ice pellets/sleet (merged into one real category - "
            "see acf.science.precipitation.HydrometeorType's own docstring). phase_severity is a real, "
            "disclosed ACF ordinal design choice (see this module's own docstring), not a published "
            "numeric severity index."
        ),
    }
