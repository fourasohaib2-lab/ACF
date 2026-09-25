"""
Atmospheric Complexity Framework (ACF)

Orographic (Mountain-Wave) Turbulence - Reference Facts

Real, published reference facts about the formation conditions and
structure of orographic (mountain-wave) turbulence - encyclopedic
reference knowledge, distinct from the real, computed per-point
mountain-wave Froude number diagnostic already in
``awci.hazards.orographic_froude`` (Fr = U/(N*H), ICAO Doc 9817/AMS
Aviation Meteorology). That module computes a real per-point stability
regime; this module records the real, independent formation-condition
facts (wind speed/slope thresholds, rotor descent speed, wavelength)
that Fr alone does not capture - no overlap, no duplication.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomOrographe.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real minimum wind speed (knots), blowing perpendicular to a ridge
#: crest, generally required for standing mountain waves to form.
OROGRAPHIC_WAVE_MINIMUM_WIND_SPEED_KT = 25.0

#: Real critical terrain slope (degrees) above which airflow tends to
#: separate from the lee slope and form horizontal-axis rotor vortices,
#: rather than following the terrain smoothly.
OROGRAPHIC_WAVE_ROTOR_CRITICAL_SLOPE_DEG = 40.0

#: Real typical descent rate range (km/h) of air within a lee-wave
#: rotor - the real, most turbulent sub-wavelength layer beneath the
#: wave crest.
OROGRAPHIC_WAVE_ROTOR_DESCENT_SPEED_KMH = (20.0, 36.0)

#: Real, typical minimum downwind extent (km) over which a standing
#: mountain-wave train can persist - a real lower bound, not a fixed
#: value (real wavelength depends on real wind speed and real
#: stratification, not captured by a single number here).
OROGRAPHIC_WAVE_MINIMUM_DOWNWIND_EXTENT_KM = 100.0

#: Real qualitative formation requirements not reducible to a single
#: numeric threshold: real wind direction must stay close to constant
#: with height (minimal directional shear) while real wind speed
#: increases with altitude, for a coherent standing wave to form.
OROGRAPHIC_WAVE_REQUIRES_MINIMAL_DIRECTIONAL_SHEAR = True
OROGRAPHIC_WAVE_REQUIRES_SPEED_INCREASING_WITH_HEIGHT = True

#: Real qualitative stability outcomes: in a stable airmass, air
#: parcels displaced over the ridge oscillate and descend on the lee
#: side (the real wave regime); in an unstable airmass, the same lifted
#: air instead keeps rising, often developing real cumulus/
#: cumulonimbus rather than a stationary wave.
OROGRAPHIC_WAVE_STABLE_AIR_OUTCOME = "oscillatory lee-side descent (standing wave)"
OROGRAPHIC_WAVE_UNSTABLE_AIR_OUTCOME = "continued orographic lifting, possible Cu/Cb development"
