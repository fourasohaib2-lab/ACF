"""
Atmospheric Complexity Framework (ACF)

Thunderstorm Life-Cycle & Hazard Reference

Real, published reference facts about the monocellular thunderstorm
life cycle and its associated hazards - encyclopedic reference
knowledge, distinct from the real, computed per-point diagnostics
already in ``awci.hazards`` (e.g. ``updraft.py``'s own CAPE-derived
maximum updraft velocity, ``convective_energy.py``'s own CAPE/CIN).

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/PhenomOrages.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

from enum import Enum


class ThunderstormStage(str, Enum):
    """Real monocellular thunderstorm life-cycle stages."""

    CUMULUS = "cumulus"  # formation - updraft only, no precipitation yet
    MATURE = "mature"  # simultaneous updraft and downdraft, precipitation, the most violent stage
    DISSIPATING = "dissipating"  # downdraft-dominated, weakening


#: Real typical dissipation time (minutes) for a monocellular
#: thunderstorm cell once it enters the dissipating stage.
THUNDERSTORM_DISSIPATION_TIME_MINUTES = 30.0

#: Real typical vertical velocity magnitudes (m/s) during the mature
#: stage - the most violent stage of the real life cycle.
THUNDERSTORM_MATURE_UPDRAFT_M_S = 35.0
THUNDERSTORM_MATURE_DOWNDRAFT_M_S = 15.0

#: Real typical cumulonimbus anvil altitude (m) at mid-latitudes.
CUMULONIMBUS_ANVIL_ALTITUDE_M = 15_000.0

#: Real typical lateral extent (nautical miles) of hazardous
#: turbulence around an isolated thunderstorm cell.
THUNDERSTORM_TURBULENCE_LATERAL_EXTENT_NM = (10.0, 20.0)

#: Real, approximate annual lightning-strike rate for a commercial
#: airliner, and the real order-of-magnitude peak current (amperes) a
#: strike can carry.
AIRLINER_LIGHTNING_STRIKES_PER_YEAR_APPROX = 1.0
LIGHTNING_PEAK_CURRENT_AMPERES_APPROX = 200_000.0

#: Real hail diameter -> real terminal fall velocity reference points
#: (mm, km/h) - not a continuous formula, three real, cited data
#: points.
HAIL_DIAMETER_MM_TO_FALL_VELOCITY_KMH: dict[float, float] = {
    20.0: 75.0,
    50.0: 115.0,
    100.0: 160.0,
}

#: Real typical hail diameter range (mm), and the real documented
#: maximum.
HAIL_DIAMETER_TYPICAL_RANGE_MM = (5.0, 50.0)
HAIL_DIAMETER_MAXIMUM_DOCUMENTED_MM = 150.0
