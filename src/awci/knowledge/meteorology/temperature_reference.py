"""
Atmospheric Complexity Framework (ACF)

Temperature Reference Facts

Real, published reference facts about temperature: unit conversion
anchors, real observed temperature values at each atmospheric layer's
boundary, the real typical/possible altitude range of subsidence
temperature inversions, a real illustrative wind-chill example, and
Earth's real axial tilt (the real, cited driver of seasonal temperature
variation this source itself gives).

Real, disclosed discrepancy: this source's real observed mesosphere
minimum temperature (-73 to -80 degC) is a DIFFERENT real, cited value
from ``awci.knowledge.meteorology.atmosphere_composition.
MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX`` (-100 degC, cited from a
different lavionnaire.fr page, MeteoAtmosphere.php) - both are real,
independently cited values for the same real physical quantity from two
pages of the same source; kept as a separate, disclosed value rather
than silently overwriting the existing one (same discipline already
established for the icing/hydroplaning/lapse-rate discrepancies found
earlier in this session).

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoTemperature.php (a real, standard
French aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real Celsius/Kelvin conversion anchor and real absolute zero (degC).
KELVIN_ZERO_CELSIUS_OFFSET = 273.15
ABSOLUTE_ZERO_C = -273.15

#: Real observed tropopause temperature range (degC, temperate
#: latitudes) - complementary to
#: awci.knowledge.meteorology.atmosphere_composition's own real
#: tropopause ALTITUDE facts (this module adds the real TEMPERATURE at
#: that altitude, a different physical quantity).
TROPOPAUSE_TEMPERATURE_RANGE_C_TEMPERATE = (-56.0, -55.0)

#: Real observed stratopause temperature range (degC) - consistent
#: with (not duplicating) the existing
#: atmosphere_composition.STRATOPAUSE_TEMPERATURE_K_APPROX (270 K =
#: -3.15 degC, within this real range).
STRATOPAUSE_TEMPERATURE_RANGE_C = (-3.0, 0.0)

#: Real, disclosed ALTERNATE-source mesosphere minimum temperature
#: range (degC) - see module docstring's discrepancy disclosure.
MESOSPHERE_MINIMUM_TEMPERATURE_RANGE_C_ALTERNATE_SOURCE = (-80.0, -73.0)

#: Real typical, and real possible (wider), altitude range (feet) for a
#: subsidence temperature inversion.
SUBSIDENCE_INVERSION_TYPICAL_ALTITUDE_RANGE_FT = (8_000.0, 12_000.0)
SUBSIDENCE_INVERSION_POSSIBLE_ALTITUDE_RANGE_FT = (5_000.0, 18_000.0)

#: Real, cited illustrative wind-chill example (not a general formula -
#: this source gives one worked example, not the underlying wind-chill
#: equation): a real air temperature/wind speed pair and the real
#: resulting perceived temperature.
WIND_CHILL_EXAMPLE_AIR_TEMPERATURE_C = -10.0
WIND_CHILL_EXAMPLE_WIND_SPEED_KMH = 30.0
WIND_CHILL_EXAMPLE_PERCEIVED_TEMPERATURE_C = -20.0

#: Real Earth axial tilt (degrees) relative to the orbital plane - the
#: real, cited driver of seasonal temperature variation.
EARTH_AXIAL_TILT_DEG = 23.27
