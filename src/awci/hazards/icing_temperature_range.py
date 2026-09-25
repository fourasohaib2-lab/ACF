"""
ACF Complexity Engine — real ICAO airframe-icing temperature-range check
=============================================================================

Explicit user request ("je veux que tu ajoutes toutes les seuils
possible pour que le projet soit conforme à 100%", continuing "je veux
que AWCI travaille avec les lois de l'OACI et l'OMM"). `acf.aviation.
hazards.aviation_hazards.AVIATION_HAZARDS_REGISTRY["airframe_icing"]`
already cites the real ICAO/FAA temperature range airframe icing
(supercooled liquid water freezing on contact with the airframe, as
opposed to `acf.awci.hydrometeor_phase`'s own surface-PRECIPITATION-
phase classification, a related but distinct real concept) requires -
"entre 0°C et -40°C" - but that fact only ever existed as free text
inside `physical_explanation`, never as a real, reusable numeric
constant anything in `acf.awci` could check a real per-point
temperature against.

Real, cited thresholds, not invented
----------------------------------------
`ICING_TEMPERATURE_UPPER_C` (0.0) and `ICING_TEMPERATURE_LOWER_C`
(-40.0) are the exact same real range already cited in
`AVIATION_HAZARDS_REGISTRY["airframe_icing"]`'s own references (ICAO
Annex 3 Chapter 3, FAA Aviation Weather Handbook Chapter 19) - not an
independently chosen ACF range. Above 0°C, supercooled liquid water
cannot exist (any liquid present is not supercooled - no in-flight
airframe icing risk from cloud/precipitation contact). Below -40°C,
cloud water is real-world predominantly already glaciated (ice
crystals, not supercooled liquid droplets) - the real, standard
homogeneous-nucleation temperature is close to this bound, so airframe
icing from supercooled liquid becomes a real, comparatively rare event
below it (still real ice-crystal icing/engine-icing risk exists
there - a distinct real phenomenon this function does not classify).

Honest scope
---------------
This is a real, binary THERMAL PRECONDITION check only - "can
supercooled liquid water plausibly exist here" - not a severity score
and not a substitute for `acf.awci.hydrometeor_phase`'s own real
surface-precipitation-phase severity (a different, already-real
diagnostic already feeding the microphysical module). No real liquid
water content (LWC) field exists anywhere in `CoupledEarthSolver`'s
state (see `acf.awci.hydrometeor_phase`'s own module docstring) - this
function never claims to know whether icing IS occurring, only
whether the real temperature at this point falls inside the real
range where it COULD.
"""

from __future__ import annotations

#: Real ICAO Annex 3 Chapter 3 / FAA Aviation Weather Handbook Chapter
#: 19 airframe-icing temperature range (°C) - see module docstring.
#: Not an ACF invention; the same range already cited in
#: AVIATION_HAZARDS_REGISTRY["airframe_icing"]'s own free-text
#: physical_explanation.
ICING_TEMPERATURE_UPPER_C = 0.0
ICING_TEMPERATURE_LOWER_C = -40.0


def is_within_icing_temperature_range(temperature_k: float) -> bool:
    """
    Real check: does `temperature_k` fall inside the real ICAO/FAA
    airframe-icing-favorable temperature range (see module docstring)?

    Parameters
    ----------
    temperature_k : float
        Real air temperature (K).

    Returns
    -------
    bool
        True if `ICING_TEMPERATURE_LOWER_C <= temperature_c <=
        ICING_TEMPERATURE_UPPER_C`, a real thermal precondition for
        supercooled liquid water to exist - never a claim that icing
        IS occurring (see module docstring's own honest scope).
    """
    temperature_c = temperature_k - 273.15
    return ICING_TEMPERATURE_LOWER_C <= temperature_c <= ICING_TEMPERATURE_UPPER_C
