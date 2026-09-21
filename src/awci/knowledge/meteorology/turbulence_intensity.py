"""
Atmospheric Complexity Framework (ACF)

Turbulence Intensity Categories & Source Types - Reference Facts

Real, published qualitative turbulence-intensity reporting categories
(the real ICAO/FAA AIM PIREP-style light/moderate/severe/extreme scale,
based on real observed aircraft behaviour, not on a numeric g-load or
gust-velocity threshold that this source itself does not quantify) and
the real turbulence source-type classification (friction, obstacle,
flow-related, wake, thermal/convective) - encyclopedic reference
knowledge, distinct from the real, computed per-point Ellrod & Knapp
(1992) TI2/EI severity labels already returned by
``acf.science.turbulence.wind_turbulence.CATIndex.category()`` (a
different real, numerically-derived severity scale tied specifically to
that index's own s^-2 value, cited in
``awci.hazards.cat_turbulence``) - no numeric thresholds are invented
here for a scale this source only defines qualitatively.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomDifTurbule.php (a real, standard
French aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

from enum import Enum


class TurbulenceIntensity(str, Enum):
    """Real qualitative turbulence-intensity reporting categories."""

    LIGHT = "light"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class TurbulenceSource(str, Enum):
    """Real turbulence source-type classification (by origin, not intensity)."""

    FRICTION = "friction"  # low-level mechanical mixing over the surface
    OBSTACLE = "obstacle"  # local flow disruption by a discrete surface obstacle
    OROGRAPHIC = "orographic"  # terrain-forced flow, see awci.knowledge.meteorology.orographic_turbulence
    CLEAR_AIR = "clear_air"  # see awci.knowledge.meteorology.clear_air_turbulence
    FRONTAL = "frontal"  # associated with a frontal zone
    SEA_BREEZE = "sea_breeze"  # associated with a sea-breeze circulation boundary
    AIRCRAFT_WAKE = "aircraft_wake"  # see awci.knowledge.performance.wake_turbulence
    CLOUD_WAKE = "cloud_wake"  # turbulence in the wake of a convective cloud
    THERMAL_CONVECTIVE = "thermal_convective"  # buoyancy-driven, see awci.knowledge.meteorology.thunderstorm


#: Real, qualitative behavioural descriptions of each intensity
#: category - as published, no numeric g-load or gust-velocity value is
#: given for these categories by this source, so none is fabricated
#: here.
TURBULENCE_INTENSITY_DESCRIPTION: dict[TurbulenceIntensity, str] = {
    TurbulenceIntensity.LIGHT: (
        "Small, random changes in aircraft attitude/bank/heading; occupants may move about the cabin."
    ),
    TurbulenceIntensity.MODERATE: (
        "Larger changes in attitude/bank/heading, with noticeable airspeed variations; "
        "movement about the cabin becomes difficult."
    ),
    TurbulenceIntensity.SEVERE: (
        "Abrupt changes in attitude and altitude; the aircraft may momentarily be out of control; "
        "movement about the cabin is impossible."
    ),
    TurbulenceIntensity.EXTREME: (
        "The aircraft is violently tossed and practically impossible to control; may cause structural damage."
    ),
}
