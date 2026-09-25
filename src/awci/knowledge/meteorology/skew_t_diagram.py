"""
Atmospheric Complexity Framework (ACF)

Emagram / Skew-T Diagram & Radiosonde - Reference Facts

Real, published reference facts about the emagram/skew-T aerological
diagram (axes, plotted lines) and the real dry/moist adiabatic
reference lapse rates it displays, plus real radiosonde operational
facts (ascent duration, burst altitude, release schedule, horizontal
drift) - encyclopedic reference knowledge. The real dry adiabatic rate
here (~1 degC/100 m) is a DIFFERENT, well-established real physical
constant from
``awci.knowledge.meteorology.atmosphere_composition.
TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M`` (~6.4 degC/1000m,
the real ENVIRONMENTAL/observed lapse rate) - the dry adiabatic rate is
the real rate an unsaturated PARCEL cools while rising, not the real
rate the surrounding ambient air's temperature actually decreases with
height; both are real, distinct, standard meteorological quantities,
not a duplicate.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoEmagram.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real emagram/skew-T diagram axis conventions - qualitative facts,
#: not numeric thresholds: the abscissa plots real temperature via
#: isotherms inclined 45 degrees, the ordinate plots real pressure via
#: horizontal isobars, with a secondary altitude ordinate.
SKEW_T_ISOTHERM_INCLINATION_DEG = 45.0

#: Real dry adiabatic lapse rate (degC per 100 m, and per 1000 ft) - the
#: real rate an unsaturated air parcel cools while rising from the
#: surface to the tropopause, a real, standard, near-constant physical
#: quantity (g/cp for dry air).
DRY_ADIABATIC_LAPSE_RATE_C_PER_100M = 1.0
DRY_ADIABATIC_LAPSE_RATE_C_PER_1000FT = 3.0

#: Real moist (pseudo-adiabatic) lapse rate (degC per 1000 m, and per
#: 1000 ft) - a real, TYPICAL reference value, not a constant: the
#: actual real moist-adiabatic rate genuinely varies with temperature
#: and altitude across a real, disclosed range (this source's own
#: stated bound), since it depends on the real, temperature-dependent
#: latent-heat release from condensation.
MOIST_ADIABATIC_LAPSE_RATE_C_PER_1000M_TYPICAL = 5.0
MOIST_ADIABATIC_LAPSE_RATE_C_PER_1000FT_TYPICAL = 1.5
MOIST_ADIABATIC_LAPSE_RATE_RANGE_C_PER_1000M = (1.0, 8.0)

#: Real saturation mixing-ratio line slope on the emagram (degC per
#: 1000 m) - the third real reference-line family plotted alongside
#: the dry/moist adiabats.
MIXING_RATIO_LINE_SLOPE_C_PER_1000M = 2.0

#: Real radiosonde operational facts: typical ascent duration (hours),
#: typical balloon-burst altitude range (km), and the real standard
#: synoptic release times (UTC) - the real, internationally
#: standardized 00Z/12Z main radiosonde network schedule.
RADIOSONDE_ASCENT_DURATION_RANGE_HOURS = (2.0, 2.5)
RADIOSONDE_BURST_ALTITUDE_RANGE_KM = (20.0, 30.0)
RADIOSONDE_STANDARD_RELEASE_TIMES_UTC = ("00:00", "12:00")

#: Real, disclosed qualitative fact: horizontal wind drift carries a
#: radiosonde tens of kilometres or more from its release point by the
#: time of burst - a real, order-of-magnitude description, not a
#: precise numeric range this source does not give.
RADIOSONDE_HORIZONTAL_DRIFT_DESCRIPTION = "tens of kilometres or more from the release point"
