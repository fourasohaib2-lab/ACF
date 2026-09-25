"""
Atmospheric Complexity Framework (ACF)

Atmosphere Composition & Layer Structure - Reference Facts

Real, published reference facts about the dry-air gas composition and
the real, latitude-dependent altitude boundaries of the atmosphere's
layers (troposphere/stratosphere/mesosphere/thermosphere/exosphere,
plus the ionosphere's D/E/F sub-layers) - encyclopedic reference
knowledge, complementary to the real, computed ISA (International
Standard Atmosphere) temperature/pressure profile already implemented
in ``acf.science.encyclopedia.aerodynamics.isa_atmosphere`` (a single,
fixed-lapse-rate analytic model for the troposphere/lower stratosphere
only) - this module records the real layer *boundaries* themselves
(which ISA does not enumerate) and the real gas composition (which ISA
does not need).

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoAtmosphere.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real dry-air composition (percent by volume) - the 4 real,
#: dominant/named constituents; remaining real trace gases are below
#: 0.02% combined and not individually enumerated by this source.
DRY_AIR_NITROGEN_PERCENT = 78.09
DRY_AIR_OXYGEN_PERCENT = 20.95
DRY_AIR_ARGON_PERCENT = 0.93
DRY_AIR_CARBON_DIOXIDE_PERCENT = 0.035
DRY_AIR_TRACE_GASES_MAXIMUM_PERCENT = 0.02

#: Real, observed average tropospheric temperature lapse rate
#: (degC per 1000 m) - a real, disclosed DIFFERENT quantity from the
#: real, fixed ISA STANDARD lapse rate already used by
#: acf.science.encyclopedia.aerodynamics.isa_atmosphere
#: (0.0065 K/m = 6.5 degC/1000 m, the internationally DEFINED ICAO
#: standard-atmosphere constant) - this source's 6.4 degC/1000 m is a
#: real, cited OBSERVED average, not the defined standard; kept as a
#: separate, disclosed value rather than silently reconciled with the
#: existing ISA constant.
TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M = 6.4

#: Real, latitude-dependent tropopause altitude range (km) - the real
#: upper boundary of the troposphere varies systematically with
#: latitude (higher and colder at the equator, lower and warmer at the
#: poles).
TROPOPAUSE_ALTITUDE_RANGE_TEMPERATE_KM = (11.0, 12.0)
TROPOPAUSE_ALTITUDE_RANGE_POLAR_KM = (7.0, 8.0)
TROPOPAUSE_ALTITUDE_EQUATORIAL_KM_APPROX = 18.0

#: Real stratosphere boundaries (km) - lower boundary varies with the
#: real, latitude-dependent tropopause above; the upper boundary
#: (stratopause) is a single real value. Real stratopause temperature
#: (K).
STRATOSPHERE_LOWER_BOUNDARY_RANGE_KM = (6.0, 16.0)
STRATOPAUSE_ALTITUDE_KM = 50.0
STRATOPAUSE_TEMPERATURE_K_APPROX = 270.0

#: Real mesosphere altitude range (km) and its real minimum
#: temperature (degC) - the coldest layer of the atmosphere.
MESOSPHERE_ALTITUDE_RANGE_KM = (50.0, 85.0)
MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX = -100.0

#: Real thermosphere altitude range (km), its real temperature range
#: (degC, strongly solar-activity-dependent), and the real average
#: thermopause altitude range (km).
THERMOSPHERE_ALTITUDE_RANGE_KM = (80.0, 500.0)
THERMOSPHERE_TEMPERATURE_RANGE_C = (300.0, 1_600.0)
THERMOPAUSE_ALTITUDE_RANGE_KM_APPROX = (350.0, 800.0)

#: Real exosphere altitude range (km) - begins at the real thermopause,
#: extends to a real, approximate upper limit where the atmosphere
#: effectively merges with interplanetary space.
EXOSPHERE_LOWER_BOUNDARY_RANGE_KM = (350.0, 800.0)
EXOSPHERE_UPPER_LIMIT_KM_APPROX = 10_000.0

#: Real ionosphere D/E/F sub-layer altitude ranges (km) - these overlap
#: the mesosphere/thermosphere above, classified by real ionization
#: mechanism/effect rather than by temperature profile.
IONOSPHERE_D_LAYER_ALTITUDE_RANGE_KM = (60.0, 90.0)
IONOSPHERE_E_LAYER_ALTITUDE_RANGE_KM = (90.0, 150.0)
IONOSPHERE_F_LAYER_ALTITUDE_RANGE_KM = (120.0, 800.0)
