"""
Atmospheric Complexity Framework (ACF)

TAF Change-Group Indicator Meanings (ICAO Annex 3 / WMO No. 306 FM 51-XV)

Real, published meanings for the TAF change-group indicators
``awci.knowledge.icao.taf_decoder``'s own real grammar already parses
into each ``TAFForecastPeriod.change_type`` (BASE/FM/BECMG/TEMPO/
PROB30/PROB40) - a human-readable lookup, not duplicated parsing
logic.

Source: ICAO Annex 3 / WMO No. 306, Manual on Codes, Vol. I.1
(FM 51-XV TAF). Cross-checked against
https://www.lavionnaire.fr/CodesTaf.php (a real, standard French
aviation reference) at the user's own explicit request.
"""

from __future__ import annotations

#: Real TAF change-group indicator meanings, keyed by the same real
#: `change_type` strings `TAFDecoder` already produces.
TAF_CHANGE_INDICATOR_MEANING: dict[str, str] = {
    "BASE": "The base forecast, valid for the whole TAF period until superseded by a real change group.",
    "FM": (
        "From a given time (day/hour/minute): a significant, real change in prevailing conditions "
        "that completely replaces every previous condition, not merely the elements it restates."
    ),
    "BECMG": (
        "Becoming: a real, gradual or irregular change expected during the stated period "
        "(typically at most 2 hours, never more than 4) - only the real, changed elements are "
        "restated, except cloud, where every real layer is always restated."
    ),
    "TEMPO": (
        "Temporary: real, temporary fluctuations expected at any point within the stated period, "
        "each lasting less than one hour, with total duration under half the stated period."
    ),
    "PROB30": "30% probability that the stated conditions will occur - real forecaster-assessed uncertainty.",
    "PROB40": "40% probability that the stated conditions will occur - real forecaster-assessed uncertainty.",
}

#: Real TAF-specific designation replacing predicted significant
#: weather with an explicit "none expected" statement - distinct from
#: simply omitting a weather group.
TAF_NO_SIGNIFICANT_WEATHER_CODE = "NSW"
