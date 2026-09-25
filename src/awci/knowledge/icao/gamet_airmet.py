"""
Atmospheric Complexity Framework (ACF)

GAMET & AIRMET - Low-Altitude Area Forecast/Warning Reference

Real, published ICAO/WMO reference information on GAMET (a real,
abbreviated-plain-language low-altitude area FORECAST for a given
Flight Information Region) and AIRMET (a real, abbreviated-plain-
language low-altitude WARNING for phenomena not already covered by
the latest GAMET) - complementary to SIGMET (see
``awci.knowledge.icao.sigmet_decoder``/``sigmet_validity``), which
covers higher-severity phenomena across all altitudes.

Deliberately not a decoder (unlike ``metar_decoder``/``taf_decoder``/
``sigmet_decoder``): real GAMET/AIRMET altitude coverage and even
whether they are coded at all is genuinely State-specific (e.g.
France does not code GAMET/AIRMET at all), so there is no single, real
universal grammar to parse the way METAR/TAF/SIGMET have one - this
module records only the real, State-independent facts.

Source: ICAO Annex 3 to the Convention on International Civil
Aviation. Cross-checked against
https://www.lavionnaire.fr/CodesGamAir.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real, State-independent AIRMET criterion: surface wind gusts at or
#: above this speed warrant an AIRMET (if not already covered by the
#: latest GAMET).
AIRMET_SURFACE_WIND_GUST_THRESHOLD_KT = 40.0

#: Real AIRMET phenomena categories (non-convective moderate icing/
#: turbulence/orographic waves, isolated-to-frequent thunderstorms
#: with or without hail, snow showers, freezing rain, strong surface
#: gusts) - real, but only issued for phenomena NOT already present in
#: the latest real GAMET for the same area/period.
AIRMET_PHENOMENA = (
    "surface wind gusts >= 40 kt",
    "isolated to frequent thunderstorms (with or without hail)",
    "snow showers",
    "freezing rain",
    "moderate icing (non-convective)",
    "moderate turbulence (non-convective)",
    "moderate orographic waves",
)
