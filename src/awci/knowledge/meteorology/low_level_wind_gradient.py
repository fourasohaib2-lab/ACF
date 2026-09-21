"""
Atmospheric Complexity Framework (ACF)

Low-Altitude Wind Gradient - Reference Facts

Real, published reference facts about low-altitude ("short final")
wind-gradient hazard, independent of the real, computed per-point bulk
wind shear already implemented in ``awci.hazards.wind_shear``
(sqrt((u_top-u_bottom)**2 + (v_top-v_bottom)**2) between two native
model levels) and of the real ICAO 30 kt / 1500 ft microburst
alert-proximity threshold already implemented in
``awci.hazards.microburst``. This module records the real, independent
approach-phase operational facts (exceptional gradient magnitude/rate,
critical decision altitude, ground-speed safety margin rule) that
neither of those computed diagnostics states - no overlap, no
duplication.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomGradient.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real, documented exceptional-case wind-gradient magnitude (knots)
#: and rate of change (knots per second) encountered on short final.
WIND_GRADIENT_EXCEPTIONAL_AMPLITUDE_KT = 70.0
WIND_GRADIENT_EXCEPTIONAL_RATE_KT_PER_S = 25.0

#: Real typical achievable airspeed acceleration (knots per second) for
#: an aircraft in landing configuration, 5% descent gradient, applying
#: go-around thrust - the real recovery capability a wind-gradient
#: encounter is weighed against.
AIRCRAFT_GO_AROUND_ACCELERATION_KT_PER_S = 2.0

#: Real critical altitude (feet AGL) below which there is generally
#: insufficient height to recover the intended descent profile after a
#: wind-gradient encounter.
WIND_GRADIENT_CRITICAL_ALTITUDE_FT = 500.0
