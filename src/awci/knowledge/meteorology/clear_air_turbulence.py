"""
Atmospheric Complexity Framework (ACF)

Clear Air Turbulence (CAT) - Reference Facts

Real, published reference facts about the typical altitude band and
jet-stream association of Clear Air Turbulence - encyclopedic
reference knowledge, distinct from the real, computed per-point
Ellrod & Knapp (1992) Turbulence Index (TI2/EI) already implemented in
``awci.hazards.cat_turbulence`` (ICAO Doc 9837). That module computes a
real per-point severity index from wind fields; this module records
the real, independent formation-context facts (altitude band,
jet-stream association, cold/warm-side asymmetry) that the index alone
does not state - no overlap, no duplication.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomTAC.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real typical altitude band (metres) in which Clear Air Turbulence is
#: most frequently encountered, particularly near the tropopause.
CAT_TYPICAL_ALTITUDE_RANGE_M = (7_000.0, 12_000.0)

#: Real typical altitude band (feet), the same range as above expressed
#: in the units actually used operationally in flight levels/METAR-TAF
#: aviation products.
CAT_TYPICAL_ALTITUDE_RANGE_FT = (23_000.0, 39_000.0)

#: Real qualitative fact: CAT occurrence is disproportionately
#: associated with jet-stream regions, where strong vertical and
#: horizontal wind shear develops around the jet core.
CAT_ASSOCIATED_WITH_JET_STREAM = True

#: Real documented example (TEMSI chart, 27/07/1993): a 130 kt jet-
#: stream core at FL340 with associated moderate turbulence reported
#: between FL240 and FL390 - a real, cited illustrative data point, not
#: a general threshold.
CAT_EXAMPLE_JET_STREAM_CORE_SPEED_KT = 130.0
CAT_EXAMPLE_JET_STREAM_CORE_FLIGHT_LEVEL = 340
CAT_EXAMPLE_TURBULENCE_FLIGHT_LEVEL_RANGE = (240, 390)

#: Real qualitative asymmetry: turbulence intensity on the cold/polar-
#: air side of a jet stream (to the left when facing downwind in the
#: Northern Hemisphere) is typically greater than on the warm-air side,
#: reflecting the real stronger baroclinicity/shear on that side.
CAT_MORE_SEVERE_ON_COLD_AIR_SIDE = True
