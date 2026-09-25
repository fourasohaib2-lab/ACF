"""
Atmospheric Complexity Framework (ACF)

Aircraft Icing Type & Intensity Classification

Real, published aviation-meteorology classification of airframe icing
by physical type (formation mechanism) and by intensity (accumulation
rate). Complementary to, and distinct from,
`awci.hazards.icing_temperature_range`'s own real binary thermal-
precondition check (can supercooled liquid water plausibly exist at
this temperature) - this module is reference/classification knowledge,
not a per-point diagnostic.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomGivrage.php (a real, standard French
aviation reference) at the user's own explicit request.

**A real, disclosed discrepancy, not silently resolved**: this source
gives -35°C as the real temperature below which icing potential is
negligible ("potentiel givrant est nul en dessous de -35°C"), while
`awci.hazards.icing_temperature_range.ICING_TEMPERATURE_LOWER_C`
already cites -40°C, sourced from ICAO Annex 3 Chapter 3 / the FAA
Aviation Weather Handbook Chapter 19. Both are real, cited figures
from real sources describing the same real physical phenomenon
(supercooled liquid water becoming rare as homogeneous ice nucleation
dominates) with a genuine ~5°C difference in exactly where the
threshold is drawn - not a project inconsistency to paper over. The
existing `awci.hazards` module's ICAO/FAA-sourced -40°C is kept as
the real, unchanged operational threshold; this module's own -35°C is
recorded here as this specific source's own real figure, not merged
or silently overridden.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

#: Real temperature range (°C) within which supercooled liquid water
#: is most abundant in cloud, per this source - the real peak-icing
#: layer, distinct from (narrower than) the full -40°C to 0°C
#: ICAO/FAA precondition range already used in
#: awci.hazards.icing_temperature_range.
PEAK_ICING_LAYER_UPPER_C = 0.0
PEAK_ICING_LAYER_LOWER_C = -15.0

#: Real, disclosed alternate lower bound for icing potential from this
#: specific source (see module docstring for the discrepancy against
#: the already-real -40°C ICAO/FAA value used elsewhere in this
#: codebase).
ICING_POTENTIAL_NEGLIGIBLE_BELOW_C = -35.0

#: Real, disclosed real-world extension of icing risk in strong
#: convective updrafts, where liquid water can be lofted well below
#: the peak layer before fully glaciating.
CONVECTIVE_ICING_POTENTIAL_LOWER_C = -20.0


class IcingIntensity(str, Enum):
    """Real aviation-meteorology icing intensity categories, by ice
    accretion rate."""

    LIGHT = "light"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass(frozen=True)
class IcingIntensityThreshold:
    """Real minimum ice-accretion rate (g/cm^2 per hour) for one
    icing intensity category, and its real operational meaning."""

    minimum_accretion_rate_g_cm2_per_hour: float
    operational_meaning: str


#: Real icing intensity classification by ice accretion rate,
#: source-cited (see module docstring).
ICING_INTENSITY_THRESHOLDS: dict[IcingIntensity, IcingIntensityThreshold] = {
    IcingIntensity.LIGHT: IcingIntensityThreshold(
        minimum_accretion_rate_g_cm2_per_hour=1.0,
        operational_meaning="Does not require special flight-control measures.",
    ),
    IcingIntensity.MODERATE: IcingIntensityThreshold(
        minimum_accretion_rate_g_cm2_per_hour=6.0,
        operational_meaning="May prompt the crew to change heading or altitude.",
    ),
    IcingIntensity.SEVERE: IcingIntensityThreshold(
        minimum_accretion_rate_g_cm2_per_hour=12.0,
        operational_meaning="Demands an immediate heading or altitude change.",
    ),
}


class IcingType(str, Enum):
    """Real airframe icing types, by formation mechanism."""

    RIME = "rime"
    CLEAR = "clear"
    MIXED = "mixed"
    GLAZE = "glaze"


#: Real, qualitative formation-condition description for each real
#: icing type - not itself a numeric threshold table (formation
#: mechanism, not a measured rate), source-cited (see module
#: docstring).
ICING_TYPE_FORMATION: dict[IcingType, str] = {
    IcingType.RIME: (
        "Supercooled droplets freeze rapidly on contact - opaque, brittle ice, "
        "typically light to moderate intensity."
    ),
    IcingType.CLEAR: (
        "Supercooled droplets spread and freeze slowly, near 0 degC with high "
        "liquid water content - typically moderate to severe intensity."
    ),
    IcingType.MIXED: "A heterogeneous blend of clear and rime ice layers - typically moderate to severe intensity.",
    IcingType.GLAZE: (
        "Forms from freezing rain or freezing drizzle (large supercooled droplets) - typically severe intensity."
    ),
}
