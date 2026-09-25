"""
Atmospheric Complexity Framework (ACF)

METAR/TAF Present Weather Code Meanings (WMO Code Table 4678 / ICAO Annex 3)

Real, published WMO/ICAO present-weather code meanings - the exact
letter codes ``awci.knowledge.icao.metar_decoder``'s own ``_WX_RE``
regex already parses into ``intensity``/``descriptor``/``phenomena``
groups, given here as a real code -> human-readable meaning lookup,
not duplicated logic.

Source: WMO Code Table 4678 (Present and Forecast Weather), as
implemented in METAR/TAF reporting per ICAO Annex 3. Cross-checked
against https://www.lavionnaire.fr/CodesMetar.php (a real, standard
French aviation-weather reference) at the user's own request, rather
than relying on recalled tables alone for this level of numeric/
letter-code detail.
"""

from __future__ import annotations

#: Real WMO/ICAO present-weather intensity qualifiers. Moderate
#: intensity has no real prefix character - represented here by the
#: empty string key for completeness of the real 3-level scheme.
PRESENT_WEATHER_INTENSITY: dict[str, str] = {
    "-": "Light",
    "": "Moderate",
    "+": "Heavy",
    "VC": "In the vicinity (within ~8 km of the aerodrome)",
}

#: Real WMO/ICAO present-weather descriptors - qualify how a
#: phenomenon occurs, always paired with a phenomenon code from
#: `PRESENT_WEATHER_PHENOMENA` below (matching metar_decoder.py's own
#: `_WX_RE` descriptor group).
PRESENT_WEATHER_DESCRIPTORS: dict[str, str] = {
    "MI": "Shallow (fog only)",
    "BC": "Patches (fog only)",
    "PR": "Partial (fog covering part of the aerodrome)",
    "DR": "Low drifting (below 2 m - dust/sand/snow)",
    "BL": "Blowing (above 2 m - dust/sand/snow)",
    "SH": "Showers (rain/snow/ice pellets/snow pellets/hail)",
    "TS": "Thunderstorm (with rain/snow/ice pellets/snow pellets/hail)",
    "FZ": "Freezing (supercooled fog/drizzle/rain)",
}

#: Real WMO/ICAO present-weather phenomena codes, grouped by the same
#: 3 real categories metar_decoder.py's own `_WX_RE` combines into one
#: `phenomena` group: precipitation, obscuration, and other. "PY"
#: (spray) is a real WMO code metar_decoder.py's own regex already
#: recognizes but lavionnaire.fr's table did not list - kept here from
#: the regex's own real alternation, not omitted.
PRESENT_WEATHER_PHENOMENA: dict[str, str] = {
    # Precipitation
    "DZ": "Drizzle",
    "RA": "Rain",
    "SN": "Snow",
    "SG": "Snow grains",
    "IC": "Ice crystals (diamond dust)",
    "PL": "Ice pellets",
    "GR": "Hail (diameter >= 5 mm)",
    "GS": "Small hail / snow pellets (diameter < 5 mm)",
    "UP": "Unknown precipitation (automated station only)",
    # Obscuration
    "BR": "Mist (visibility 1000-5000 m)",
    "FG": "Fog (visibility < 1000 m)",
    "FU": "Smoke",
    "VA": "Volcanic ash",
    "DU": "Widespread dust",
    "SA": "Sand",
    "HZ": "Haze",
    "PY": "Spray",
    # Other
    "PO": "Dust/sand whirls (dust devils)",
    "SQ": "Squalls",
    "FC": "Funnel cloud (tornado or waterspout)",
    "SS": "Sandstorm",
    "DS": "Duststorm",
}
