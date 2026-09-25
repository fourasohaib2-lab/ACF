"""
Atmospheric Complexity Framework (ACF)

Squall Line / Gust Front ("Grain") - Reference Facts

Real, published reference facts about squall lines / gust fronts
("grains") - the real gust/wind-direction-shift criteria that define
one, the real macro-/micro-scale corridor-width distinction, and the
real dry/wet ("blanc"/"noir") classification - encyclopedic reference
knowledge, distinct from the real, computed per-point thunderstorm/
microburst diagnostics already in ``awci.hazards`` and from the real
thunderstorm life-cycle facts in
``awci.knowledge.meteorology.thunderstorm``.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoLesGrains.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

from enum import Enum


class SquallLineType(str, Enum):
    """Real squall-line precipitation character."""

    WHITE = "white"  # "grain blanc" - dry microburst-driven, no precipitation reaching the ground
    BLACK = "black"  # "grain noir" - wet, heavy rain accompanies the gust front


#: Real minimum wind-gust excess (knots) above the sustained mean wind
#: speed, over a real minimum measurement period, required to classify
#: a wind event as a squall ("grain").
SQUALL_MINIMUM_GUST_EXCESS_KT = 15.0
SQUALL_GUST_EXCESS_MEASUREMENT_PERIOD_MINUTES = 1.0

#: Real wind-direction shift range (degrees) typically accompanying a
#: squall-line gust front passage.
SQUALL_WIND_DIRECTION_SHIFT_RANGE_DEG = (45.0, 90.0)

#: Real typical overall event duration - a real, bounded qualitative
#: fact ("a few minutes"), not a numeric range this source itself
#: quantifies further.
SQUALL_TYPICAL_DURATION_DESCRIPTION = "a few minutes"

#: Real macro-/micro-scale gust-corridor width threshold (km) - a real
#: distinction between "macro-rafales" (wider corridor) and "micro-
#: rafales" (narrower corridor), NOT the same real quantity as
#: ``awci.knowledge.meteorology.microburst_reference.
#: MICROBURST_TYPICAL_DIAMETER_RANGE_KM`` (the physical scale of an
#: individual microburst event) - this is the real corridor-width
#: cutoff used to name the two squall-gust scales.
SQUALL_MACRO_MICRO_CORRIDOR_WIDTH_THRESHOLD_KM = 2.5
