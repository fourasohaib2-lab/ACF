"""
Atmospheric Complexity Framework (ACF)

SIGMET Message Validity Period Rules (ICAO Annex 3)

Real, published ICAO rules on how long a SIGMET message may remain
valid, and how far ahead of a real phenomenon's onset it may be
issued - reference constants, not a computed validator (real
cross-midnight day/hour arithmetic on
``awci.knowledge.icao.sigmet_decoder.SIGMETReport``'s own
``valid_from_day``/``valid_until_day`` fields is a real, separate
concern this module does not attempt).

Source: ICAO Annex 3 to the Convention on International Civil
Aviation, Meteorological Service for International Air Navigation.
Cross-checked against https://www.lavionnaire.fr/CodesSigmet.php (a
real, standard French aviation reference) at the user's own explicit
request.
"""

from __future__ import annotations

#: Real ICAO Annex 3 maximum SIGMET validity period (hours) for
#: ordinary hazardous-weather phenomena (WS SIGMET - severe
#: turbulence, severe icing, severe mountain waves, thunderstorms,
#: duststorms/sandstorms).
SIGMET_MAX_VALIDITY_HOURS_WS = 4.0

#: Real ICAO Annex 3 maximum SIGMET validity period (hours) for
#: tropical cyclone (WC SIGMET) and volcanic ash (WV SIGMET) messages -
#: real, longer-lived phenomena than the WS category above.
SIGMET_MAX_VALIDITY_HOURS_WC_WV = 6.0

#: Real ICAO Annex 3 maximum lead time (hours) a SIGMET may be issued
#: before the real onset of the phenomenon it describes, for the same
#: two real category groups above.
SIGMET_MAX_LEAD_TIME_HOURS_WS = 4.0
SIGMET_MAX_LEAD_TIME_HOURS_WC_WV = 12.0
