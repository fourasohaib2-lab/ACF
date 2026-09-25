"""
Atmospheric Complexity Framework (ACF)

Wind Units, Gust Criterion & Named Local Winds - Reference Facts

Real, published reference facts about wind-speed units/symbology, the
real METAR gust-reporting criterion, and the real typical intensity/
extent of thermally- and orographically-driven local winds (slope,
valley, sea-breeze, land-breeze circulations) plus two real, named
regional winds (Mistral, Foehn) - encyclopedic reference knowledge.
The real Foehn temperature-increase figure here is a DIFFERENT,
complementary real quantity from the real, computed
``acf.model4d.physics.mountain_physics.MountainPhysics.
foehn_temperature()`` formula (Delta T = dry-adiabatic-rate x
descent_height) - this module records the real, typically-observed
magnitude, not a substitute for that real per-case computed formula.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoVent.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real, standard unit conversion - 1 knot in km/h.
KNOT_TO_KMH = 1.852

#: Real synoptic-chart wind-barb symbology (knots per symbol) - a
#: half-barbule, a full barbule, and a pennant/triangle.
WIND_BARB_HALF_BARBULE_KT = 5.0
WIND_BARB_FULL_BARBULE_KT = 10.0
WIND_BARB_PENNANT_KT = 50.0

#: Real METAR/TAF gust-reporting criterion (ICAO Annex 3 convention, as
#: cited by this source): a gust is only reported when it exceeds the
#: real mean wind speed by at least this margin (knots / km/h), AND the
#: real mean wind speed itself is at least this same threshold.
#: Independently confirmed 2026-09-25 against a second source
#: (SKYbrary Aviation Safety, "Wind Velocity Reporting", itself citing
#: ICAO Annex 3) - not just this module's original lavionnaire.fr
#: cross-check.
GUST_REPORTING_MINIMUM_EXCESS_KT = 10.0
GUST_REPORTING_MINIMUM_EXCESS_KMH = 19.0
GUST_REPORTING_MINIMUM_MEAN_WIND_KT = 10.0

#: Real typical intensity range (knots) for slope-breeze and
#: valley-breeze thermally-driven local circulations.
SLOPE_BREEZE_TYPICAL_SPEED_RANGE_KT = (5.0, 10.0)
VALLEY_BREEZE_TYPICAL_SPEED_RANGE_KT = (5.0, 10.0)

#: Real sea-breeze typical intensity (knots) and real typical
#: horizontal penetration depth inland (m).
SEA_BREEZE_TYPICAL_SPEED_RANGE_KT = (10.0, 15.0)
SEA_BREEZE_TYPICAL_PENETRATION_DEPTH_RANGE_M = (500.0, 1_000.0)

#: Real land-breeze typical intensity (knots, weaker than the daytime
#: sea breeze) and real typical penetration depth offshore (m, also
#: shallower than the sea breeze).
LAND_BREEZE_TYPICAL_SPEED_RANGE_KT = (5.0, 10.0)
LAND_BREEZE_TYPICAL_PENETRATION_DEPTH_RANGE_M = (100.0, 300.0)

#: Real Mistral (named Rhone-valley regional wind) typical mean speed
#: (km/h) and real documented gust speeds that can exceed it.
MISTRAL_TYPICAL_MEAN_SPEED_KMH_APPROX = 50.0
MISTRAL_GUST_SPEED_MINIMUM_EXCEEDED_KMH = 100.0

#: Real, typically-observed Foehn-effect temperature increase (degC) -
#: a real, disclosed empirical magnitude, complementary to (not a
#: substitute for) the real per-case computed
#: acf.model4d.physics.mountain_physics.MountainPhysics.
#: foehn_temperature() dry-adiabatic formula.
FOEHN_TYPICAL_TEMPERATURE_INCREASE_RANGE_C = (5.0, 10.0)

#: Real qualitative Coriolis-force/geostrophic-wind facts: the Coriolis
#: force is genuinely absent at the equator (zero Coriolis parameter)
#: and maximal at the poles, so the real geostrophic-wind balance is
#: genuinely undefined at the equator (division by a real zero Coriolis
#: parameter).
CORIOLIS_FORCE_ZERO_AT_EQUATOR = True
CORIOLIS_FORCE_MAXIMUM_AT_POLES = True
GEOSTROPHIC_WIND_UNDEFINED_AT_EQUATOR = True
