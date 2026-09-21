"""
Atmospheric Complexity Framework (ACF)

Cloud Characteristics - Element Size & Special-Form Reference Facts

Real, published reference facts about cloud element angular (apparent)
width - the real WMO observational criterion actually used to tell
Cirrocumulus, Altocumulus, and Stratocumulus apart when their real
altitude étage alone is ambiguous - plus real facts about thermal
convective bubble size, pileus-formation vertical speed, and polar
stratospheric cloud dimensions. Complementary to the real genus/étage/
cover classification already in
``awci.knowledge.meteorology.clouds`` (reuses its ``CloudGenus`` enum
directly, not a second, independently-spelled name per genus).

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoNuagesCaract.php (a real, standard
French aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

from awci.knowledge.meteorology.clouds import CloudGenus

#: Real WMO apparent-width (angular size, degrees) criterion used to
#: distinguish Cirrocumulus/Altocumulus/Stratocumulus elements observed
#: from the ground - real, disjoint bands (Cc smallest, Sc largest),
#: not a continuous formula. Stratocumulus has only a real documented
#: LOWER bound (elements "exceeding 5 degrees") - no real upper bound
#: is given by this source, so none is fabricated here.
CIRROCUMULUS_ELEMENT_APPARENT_WIDTH_MAXIMUM_DEG = 1.0
ALTOCUMULUS_ELEMENT_APPARENT_WIDTH_RANGE_DEG = (1.0, 5.0)
STRATOCUMULUS_ELEMENT_APPARENT_WIDTH_MINIMUM_DEG = 5.0

#: The 3 real genera this apparent-width criterion applies to, reusing
#: the real WMO CloudGenus enum directly.
_APPARENT_WIDTH_CRITERION_GENERA = (
    CloudGenus.CIRROCUMULUS,
    CloudGenus.ALTOCUMULUS,
    CloudGenus.STRATOCUMULUS,
)

#: Real, order-of-magnitude typical diameter of a thermal convective
#: bubble - the source gives no precise numeric range, so none is
#: fabricated here.
CONVECTIVE_BUBBLE_TYPICAL_DIAMETER_DESCRIPTION = "on the order of several hundred metres"

#: Real typical vertical air speed range (km/h) associated with pileus
#: (cap cloud) formation above a growing cumulus/cumulonimbus.
PILEUS_FORMATION_VERTICAL_SPEED_RANGE_KMH = (20.0, 50.0)

#: Real polar stratospheric cloud (PSC) typical horizontal extent
#: (km, approximate) and real, order-of-magnitude vertical thickness
#: description.
POLAR_STRATOSPHERIC_CLOUD_TYPICAL_EXTENT_KM_APPROX = 100.0
POLAR_STRATOSPHERIC_CLOUD_THICKNESS_DESCRIPTION = "one to several kilometres"
