"""
Atmospheric Complexity Framework (ACF)

Jet Stream - Reference Facts

Real, published reference facts about the three real, named jet-stream
types (polar/polar-front, subtropical, equatorial easterly) - typical
core wind speed, altitude/latitude band, physical dimensions, and real
vertical/horizontal wind-shear gradients - encyclopedic reference
knowledge, complementary to the single, real cited example data point
already recorded in ``awci.knowledge.meteorology.clear_air_turbulence``
(a 130 kt jet core at FL340 from one real TEMSI chart) - that module
records one illustrative observation, this module records the general,
typical real facts for each named jet-stream type.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoJetStream.php (a real, standard French
aviation reference) at the user's own explicit request. Some real
qualitative dimensional facts (length/width/thickness) are given by
this source only as order-of-magnitude descriptions, not precise
numeric ranges - recorded here as descriptive strings rather than a
fabricated numeric range.
"""

from __future__ import annotations

from enum import Enum


class JetStreamType(str, Enum):
    """The 3 real, named jet-stream types with a confidently-cited
    real core wind-speed/altitude/latitude band in this source - a
    real, deliberately narrower set than every jet-related feature this
    source mentions (e.g. its "middle stratosphere" jets are named only
    vaguely, with no clear real type label - not included here to
    avoid mislabeling)."""

    POLAR = "polar"  # polar-front jet
    SUBTROPICAL = "subtropical"
    EQUATORIAL_EASTERLY = "equatorial_easterly"


#: Real typical physical-dimension facts - given by the source only as
#: order-of-magnitude descriptions, not precise numeric ranges.
JET_STREAM_TYPICAL_LENGTH_DESCRIPTION = "several thousand kilometres"
JET_STREAM_TYPICAL_WIDTH_DESCRIPTION = "several hundred kilometres"
JET_STREAM_TYPICAL_THICKNESS_DESCRIPTION = "only a few kilometres"

#: Real polar (polar-front) jet - occasional peak core wind speed (kt).
POLAR_JET_PEAK_WIND_SPEED_KT = 160.0
#: Real polar jet real latitude band (degrees North).
POLAR_JET_LATITUDE_RANGE_DEG = (35.0, 70.0)

#: Real subtropical jet - typical average core wind-speed range (kt),
#: and the real occasional peak.
SUBTROPICAL_JET_WIND_SPEED_RANGE_KT = (120.0, 150.0)
SUBTROPICAL_JET_PEAK_WIND_SPEED_KT = 250.0
#: Real subtropical jet core altitude range (feet).
SUBTROPICAL_JET_CORE_ALTITUDE_RANGE_FT = (35_000.0, 40_000.0)
#: Real subtropical jet winter latitude band (degrees North).
SUBTROPICAL_JET_LATITUDE_RANGE_DEG = (20.0, 40.0)

#: Real equatorial easterly jet - typical core wind-speed range (kt) at
#: its strongest, and the real typical altitude (km, ~FL450).
EQUATORIAL_EASTERLY_JET_WIND_SPEED_RANGE_KT = (80.0, 90.0)
EQUATORIAL_EASTERLY_JET_ALTITUDE_KM_APPROX = 15.0

#: Real typical vertical wind-shear gradient near a jet-stream core
#: (knots per 1000 ft), and the real typical horizontal wind-shear
#: gradient (knots per 100 nautical miles).
JET_STREAM_VERTICAL_SHEAR_KT_PER_1000FT_RANGE = (5.0, 10.0)
JET_STREAM_HORIZONTAL_SHEAR_KT_PER_100NM_RANGE = (20.0, 30.0)

#: Real cyclonic-side vs. anticyclonic-side horizontal wind-shear
#: asymmetry (knots per 100 nautical miles) - the cyclonic (cold-air,
#: cyclonic-curvature) side carries a real, steeper gradient than the
#: anticyclonic side, consistent with
#: ``awci.knowledge.meteorology.clear_air_turbulence.
#: CAT_MORE_SEVERE_ON_COLD_AIR_SIDE``.
JET_STREAM_CYCLONIC_SIDE_SHEAR_KT_PER_100NM = 45.0
JET_STREAM_ANTICYCLONIC_SIDE_SHEAR_KT_PER_100NM = 20.0
