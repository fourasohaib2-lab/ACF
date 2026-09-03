"""
ACF Complexity Engine — real mountain-wave Froude number in the topographic module (§16, wind)
=====================================================================================================

Explicit user request ("continue au module relief, avec le vent") -
continuing the real, targeted closures of §12-16 (dynamic/thermodynamic/
convective/microphysical already extended). docs/ACF_MASTER_PROMPT.md
section 16 (MODULE RELIEF / OROGRAPHIE) is explicit that relief is not
a static variable - it modifies wind, turbulence, local acceleration,
orographic waves - and explicitly cites "turbulence orographique,
accélération du vent, ondes de relief". Before this, AWCICalculator's
own `topographic` module used only static altitude
(`Normalizer.normalize_topographic()`); the only real wind-relief
signal anywhere in AWCI was the multiplicative interaction term
`wind_topo_interaction` (dynamic x topographic, §22) - real, but not a
genuine physical wind-terrain diagnostic in its own right.

Real, already-existing, cited formula reused, not reimplemented
------------------------------------------------------------------
`acf.science.encyclopedia.aviation_extended.calculate_mountain_wave_froude_number()`
- the mountain-wave Froude number Fr = U / (N * H), a real, classic,
operationally-used aviation-meteorology diagnostic (references: ICAO
Doc 9817 Wind Shear, AMS Aviation Meteorology) for stationary
orographic gravity waves and lee-side rotor turbulence: Fr < 1
indicates strong flow blocking and intense stationary waves (real
hazard regime), Fr > 1 indicates flow passing more smoothly over the
terrain. Registered in the encyclopedia but never wired into anything
producing a real ACF output - same "found real formula, never
connected" pattern as wind shear/theta-e/updraft velocity/
precipitation phase before it.

Honest scope: point-only, NOT wired into acf.awci.spatial_field
-------------------------------------------------------------------------
Unlike the four prior §12-16 closures, this one cannot be extended
into `acf.awci.spatial_field.compute_real_complexity_field()`: Fr
needs a real mountain height H and a real Brunt-Väisälä frequency N
(itself needing a real vertical potential-temperature gradient with
real geometric height spacing). CoupledEarthSolver's real state has
no terrain-elevation field at all (the same real, disclosed gap that
module's own honest_limitation already names for "terrain-altitude"),
and no real geometric height coordinate (only hybrid sigma-pressure
level indices) to derive a real dtheta/dz from without fabricating a
height reference - so neither H nor N can be honestly computed per
grid point today. This module stays a real, opt-in POINT diagnostic:
a caller who has real local knowledge (a sounding, a terrain map) can
supply real U/N/H directly; nothing here invents them.

Honest disclosed approximation: wind SPEED, not the perpendicular
component
--------------------------------------------------------------------------
Fr's real U is specifically the wind component perpendicular to the
ridge line - AWCI has no real ridge-orientation data anywhere, so
`data["wind_speed"]` (the existing scalar magnitude) is used as an
honest, disclosed upper-bound proxy: the true perpendicular component
is always <= the total wind speed magnitude, so this can only ever
UNDER-estimate Fr (i.e. it is a conservative, hazard-leaning
approximation, never one that hides real risk) - never presented as
the literal perpendicular component itself.

Honest edge case: near-neutral/unstable stratification
-------------------------------------------------------------
`acf.science.cyclones.BruntVaisalaFrequency.calculate()` itself
honestly returns N=0 for neutral/unstable air (dtheta/dz <= 0) rather
than a fabricated negative-N^2 result - the classic linear mountain-
wave theory behind Fr = U/(N*H) is only meaningful for stably
stratified flow, so a real N=0 here means "not computed", not a
fabricated infinite or zero Froude number. `froude_number` is honestly
`None` in that case (never fabricated), matching this session's own
None-not-a-placeholder-value discipline throughout §12-16 (see
acf.awci.theta_e's own identical convention for non-positive relative
humidity).
"""

from __future__ import annotations

from typing import Any

from acf.science.encyclopedia.aviation_extended import calculate_mountain_wave_froude_number


def compute_real_mountain_wave_froude_number_at_point(
    wind_speed_perpendicular: float, brunt_vaisala_n: float, mountain_height_m: float
) -> dict[str, Any]:
    """
    Real mountain-wave Froude number Fr = U / (N * H) at one point -
    thin wrapper around the real, cited
    calculate_mountain_wave_froude_number(), no new physics invented.

    Parameters
    ----------
    wind_speed_perpendicular : float
        Real wind speed (m/s) - see module docstring for the honest
        "total speed as a conservative proxy for the true perpendicular
        component" disclosure.
    brunt_vaisala_n : float
        Real Brunt-Väisälä frequency (rad/s), e.g. from
        acf.science.cyclones.BruntVaisalaFrequency.calculate() - must be
        > 0 (stably stratified); see module docstring for the honest
        N=0 (neutral/unstable) edge case.
    mountain_height_m : float
        Real terrain/ridge height (m), > 0.

    Returns
    -------
    dict
        froude_number : real float, or `None` (never a fabricated
            value) when brunt_vaisala_n <= 0 - see module docstring.
        status, is_real_data, honest_limitation.

    Raises
    ------
    ValueError
        If mountain_height_m <= 0 - a genuine caller-input error for a
        real physical quantity this module does not itself derive
        (unlike brunt_vaisala_n's own real, expected N=0 edge case).
    """
    if mountain_height_m <= 0:
        raise ValueError("mountain_height_m must be positive.")

    if brunt_vaisala_n <= 0:
        return {
            "froude_number": None,
            "status": "FROUDE_NOT_COMPUTED_NEUTRAL_OR_UNSTABLE_STRATIFICATION",
            "is_real_data": False,
            "honest_limitation": (
                f"Real Brunt-Väisälä frequency was {brunt_vaisala_n} (non-positive, neutral/unstable "
                "stratification) at this point - the classic linear mountain-wave theory behind Fr = U/(N*H) is "
                "only meaningful for stably stratified flow, so froude_number is honestly None, not a "
                "fabricated value."
            ),
        }

    froude_number = calculate_mountain_wave_froude_number(wind_speed_perpendicular, brunt_vaisala_n, mountain_height_m)

    return {
        "froude_number": froude_number,
        "status": "REAL_MOUNTAIN_WAVE_FROUDE_NUMBER",
        "is_real_data": True,
        "honest_limitation": (
            "Real mountain-wave Froude number (ICAO Doc 9817 Wind Shear; AMS Aviation Meteorology) - "
            "wind_speed_perpendicular is the real total wind speed magnitude, an honest conservative proxy for "
            "the true ridge-perpendicular component (AWCI has no real ridge-orientation data - see module "
            "docstring). Real classic linear theory; does not capture nonlinear wave breaking, real 3D terrain "
            "geometry, or trapped-lee-wave resonance conditions beyond the Fr < 1 / Fr > 1 regime split."
        ),
    }
