"""
Atmospheric Complexity Framework (ACF)

Weather Fronts - Reference Facts

Real, published reference facts about the 4 classical weather-front
types (warm, cold, occluded, stationary) - the real qualitative
movement-speed distinction, the real cloud-genus sequence each stable
front type presents (reusing
``awci.knowledge.meteorology.clouds.CloudGenus``, not a second,
independently-spelled list), and real structural facts about
occlusion and the katabatic cold front.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoFronts.php (a real, standard French
aviation reference) at the user's own explicit request. This source
gives no numeric slope ratio, temperature-gradient, or movement-speed
figure for any front type - only qualitative comparisons - so none is
fabricated here; only what the source actually states is recorded.
"""

from __future__ import annotations

from enum import Enum

from awci.knowledge.meteorology.clouds import CloudGenus


class FrontType(str, Enum):
    """The 4 real classical weather-front types."""

    WARM = "warm"
    COLD = "cold"
    OCCLUDED = "occluded"
    STATIONARY = "stationary"


#: Real qualitative movement fact: a cold front moves faster than a
#: warm front, and can overtake one (forming an occluded front - see
#: OCCLUDED_FRONT_FORMATION_DESCRIPTION below). No numeric speed is
#: given by this source for either front type.
COLD_FRONT_FASTER_THAN_WARM_FRONT = True

#: Real cloud-genus sequence (leading edge to surface passage) a
#: STABLE warm front presents, real WMO genera reused from
#: awci.knowledge.meteorology.clouds.CloudGenus.
WARM_FRONT_CLOUD_SEQUENCE: tuple[CloudGenus, ...] = (
    CloudGenus.CIRRUS,
    CloudGenus.CIRROSTRATUS,
    CloudGenus.ALTOCUMULUS,
    CloudGenus.ALTOSTRATUS,
    CloudGenus.NIMBOSTRATUS,
    CloudGenus.STRATOCUMULUS,
    CloudGenus.STRATUS,
)

#: Real cloud-genus sequence a STABLE cold front presents - a real,
#: different order/subset from the warm-front sequence above (no
#: Cumulus/Cumulonimbus here - that real unstable-cold-front variant is
#: not separately enumerated by this source beyond the katabatic-front
#: qualitative note below).
COLD_FRONT_CLOUD_SEQUENCE: tuple[CloudGenus, ...] = (
    CloudGenus.CIRRUS,
    CloudGenus.CIRROSTRATUS,
    CloudGenus.ALTOSTRATUS,
    CloudGenus.ALTOCUMULUS,
    CloudGenus.NIMBOSTRATUS,
    CloudGenus.STRATOCUMULUS,
)

#: Real qualitative persistence fact - a stationary front can persist
#: for several days without significant movement. A real, bounded
#: description, not a numeric duration this source does not give.
STATIONARY_FRONT_PERSISTENCE_DESCRIPTION = "can persist for several days without significant movement"

#: Real structural fact: an occluded front forms once a faster cold
#: front catches up to and lifts the air mass ahead of a warm front.
OCCLUDED_FRONT_FORMATION_DESCRIPTION = "forms when a cold front overtakes and lifts the air mass ahead of a warm front"

#: Real structural fact about the katabatic (dry) cold-front variant -
#: an upper-level dry-air intrusion that suppresses/disrupts convection
#: along the front, distinct from the real moist stable-cold-front
#: cloud sequence above.
KATABATIC_COLD_FRONT_FEATURE_DESCRIPTION = "upper-level dry-air intrusion disrupts convection along the front"
