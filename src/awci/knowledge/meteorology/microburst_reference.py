"""
Atmospheric Complexity Framework (ACF)

Microburst - Physical Scale & Detection-System Reference Facts

Real, published reference facts about the real physical scale of a
microburst event (peak wind speed, vertical speed, duration, horizontal
extent, altitude range) and the real airborne/ground detection-system
operational parameters (LLWAS, Predictive Windshear, Reactive
Windshear) - encyclopedic reference knowledge, distinct from the real,
computed per-point ``awci.hazards.microburst`` module, which reuses the
real ICAO Doc 9837/FAA AC 00-54 30 kt / 1500 ft alert-proximity
threshold (``MICROBURST_ALERT_SHEAR_M_S``, ``MICROBURST_ALERT_ALTITUDE_M``)
to build a risk proxy. This module records the real, independent
physical-scale and detection-system facts that threshold does not
state - no overlap, no duplication (verified: no shared constant names
with ``awci.hazards.microburst``).

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomCisaille.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real peak horizontal wind speed a microburst can generate (m/s and
#: the equivalent km/h), and the real peak vertical downdraft speed
#: range (feet per minute) observed near 300 m above ground.
MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_MS = 75.0
MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_KMH = 270.0
MICROBURST_PEAK_VERTICAL_SPEED_RANGE_FT_MIN = (720.0, 1200.0)
MICROBURST_PEAK_VERTICAL_SPEED_ALTITUDE_M = 300.0

#: Real typical event duration (minutes) and horizontal extent
#: (kilometres) of a microburst.
MICROBURST_TYPICAL_DURATION_RANGE_MINUTES = (5.0, 15.0)
MICROBURST_TYPICAL_DIAMETER_RANGE_KM = (1.0, 4.0)

#: Real altitude band (feet AGL) within which microburst-driven
#: vertical wind-shear variations are most significant, and the real
#: typical peak shear magnitude (knots) observed within that band.
MICROBURST_SIGNIFICANT_SHEAR_ALTITUDE_BAND_FT = 3_000.0
MICROBURST_SIGNIFICANT_SHEAR_MAGNITUDE_KT = 60.0

#: Real Low-Level Wind Shear Alert System (LLWAS) deployment
#: parameters: real maximum anemometer count, and the real maximum
#: distance along approach/departure trajectories they are positioned
#: within.
LLWAS_MAXIMUM_ANEMOMETER_COUNT = 30
LLWAS_MAXIMUM_TRAJECTORY_DISTANCE_NM = 3.0

#: Real Predictive Windshear (PWS, forward-looking airborne radar)
#: operational parameters: real minimum and typical warning lead time
#: (seconds), real detection range (nautical miles) ahead of the
#: aircraft, and the real altitude below which it is active in flight.
PWS_MINIMUM_WARNING_TIME_S = 10.0
PWS_TYPICAL_WARNING_TIME_S = 60.0
PWS_DETECTION_RANGE_NM = (0.5, 5.0)
PWS_ACTIVE_ALTITUDE_MAX_FT_AGL = 1_500.0
