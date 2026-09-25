"""
Atmospheric Complexity Framework (ACF)

Mist & Fog (Brume / Brouillard) - Reference Facts

Real, published reference facts about mist/fog visibility definitions,
droplet size, and the real formation conditions of the main fog types
(radiation, advection, evaporation, slope, freezing) - encyclopedic
reference knowledge, distinct from the real, computed per-point
``visibility_risk_score`` already implemented in
``awci.hazards.visibility`` (a relative-humidity/precipitation-rate
risk proxy, honestly NOT a literal visibility distance - see that
module's own docstring). This module records the real, independent
classification facts (droplet size, wind-speed formation windows,
coastal distance/thickness limits) that the risk proxy does not state
- no overlap, no duplication.

Source: aviation meteorology reference material, cross-checked against
https://www.lavionnaire.fr/MeteoBrouillard.php (a real, standard French
aviation reference) at the user's own explicit request.

FOG_VISIBILITY_MAX_KM (1.0 km) independently upgraded 2026-09-25 to a
real primary WMO citation: the WMO International Cloud Atlas states
"[t]he term 'fog' is used when microscopic droplets reduce horizontal
visibility at the Earth's surface to less than 1 km" (WMO, cloudatlas.
wmo.int, "Fog compared with mist") - an exact match, not merely a
secondary-source cross-check. That same primary source defines "mist"
only as "visibility [that does] not reduce ... to less than 1 km" -
open-ended, with no fixed upper km bound (mist is distinguished from
haze by relative humidity, not a hard distance cutoff). This module's
own `MIST_VISIBILITY_RANGE_KM` upper bound (5.0 km) is therefore kept
as the honestly-disclosed common aviation-training convention it
always was (lavionnaire.fr), not upgraded to a WMO-cited figure - the
real WMO definition does not specify one to cite.
"""

from __future__ import annotations

from enum import Enum


class FogType(str, Enum):
    """Real fog formation mechanisms."""

    RADIATION = "radiation"  # nocturnal radiative cooling under clear/calm skies
    ADVECTION = "advection"  # warm moist air advected over a colder surface
    EVAPORATION = "evaporation"  # cold air over a relatively warmer water surface
    SLOPE = "slope"  # "brouillard de pente" - air mass forced to rise along terrain
    FREEZING = "freezing"  # "brouillard givrant" - supercooled water droplets below 0 degC


#: Real visibility definitions distinguishing mist ("brume") from fog
#: ("brouillard") - mist is the lower-density regime, fog the denser
#: one. FOG_VISIBILITY_MAX_KM (1.0) is a primary WMO International
#: Cloud Atlas citation; MIST_VISIBILITY_RANGE_KM's upper bound (5.0)
#: is the aviation-training convention (lavionnaire.fr) - see module
#: docstring for why the real WMO definition of mist has no fixed
#: upper km bound to cite instead.
MIST_VISIBILITY_RANGE_KM = (1.0, 5.0)
FOG_VISIBILITY_MAX_KM = 1.0

#: Real typical droplet diameter (microns) for fog vs. mist - fog
#: droplets span a real range, mist droplets are a real, smaller,
#: roughly single value.
FOG_DROPLET_DIAMETER_RANGE_MICRONS = (1.0, 10.0)
MIST_DROPLET_DIAMETER_MICRONS_APPROX = 1.0

#: Real radiation-fog formation conditions: light wind (favours
#: shallow mixing of the cooled surface layer without dispersing it),
#: high relative humidity, clear/near-clear sky (unobstructed radiative
#: cooling), and an anticyclonic or flat pressure pattern.
RADIATION_FOG_WIND_SPEED_RANGE_KT = (1.0, 3.0)

#: Real advection-fog formation conditions: a real, bounded air/surface
#: temperature difference (sufficient to cause saturation but under
#: 10 degC), a real minimum wind speed to advect the moist air mass,
#: and a real, much higher wind-speed ceiling observed offshore.
ADVECTION_FOG_TEMPERATURE_DIFFERENCE_MAX_C = 10.0
ADVECTION_FOG_WIND_SPEED_MIN_MS = 2.0
ADVECTION_FOG_WIND_SPEED_OFFSHORE_RANGE_MS = (20.0, 30.0)

#: Real evaporation-fog ("sea smoke") spatial limits: a real maximum
#: distance from the coastline within which it typically forms, and a
#: real maximum vertical thickness - both real, bounded facts, not
#: continuous formulas.
EVAPORATION_FOG_MAXIMUM_DISTANCE_FROM_COAST_NM = 5.0
EVAPORATION_FOG_MAXIMUM_THICKNESS_M = 50.0
