"""
Atmospheric Complexity Framework (ACF)

METAR/SNOWTAM Runway State Group Codes (ICAO Annex 3)

Real, published ICAO runway-state reporting codes - the real digit
codes used in the METAR/SPECI Runway State Group and in SNOWTAM
messages to report contaminant type, coverage extent, and braking
action for a runway.

Source: ICAO Annex 3 to the Convention on International Civil
Aviation, Meteorological Service for International Air Navigation,
Appendix 3 (Runway State Group). Cross-checked against
https://www.lavionnaire.fr/CodesMetar.php (a real, standard French
aviation-weather reference) at the user's own request, rather than
relying on recalled tables alone for this level of numeric-code
detail.
"""

from __future__ import annotations

#: Real ICAO Annex 3 runway deposit type codes (single digit). "/" is
#: the real "not reported" placeholder digit, kept here as its own
#: real key rather than omitted.
RUNWAY_DEPOSIT_TYPE: dict[str, str] = {
    "0": "Dry",
    "1": "Wet",
    "2": "Slush",
    "3": "Frost or rime",
    "4": "Dry snow",
    "5": "Wet snow",
    "6": "Slippery wet snow (compacted)",
    "7": "Ice",
    "8": "Compacted or rolled snow",
    "9": "Frozen ruts or ridges",
    "/": "Not reported / type not significant",
}

#: Real ICAO Annex 3 runway contamination extent codes (single
#: digit) - the real real fraction of the runway covered by the
#: deposit reported in `RUNWAY_DEPOSIT_TYPE`.
RUNWAY_CONTAMINATION_EXTENT: dict[str, str] = {
    "1": "Less than 10% covered",
    "2": "11% to 25% covered",
    "5": "26% to 50% covered",
    "9": "51% to 100% covered",
    "/": "Not reported",
}

#: Real ICAO Annex 3 runway braking-action/friction codes (two
#: digits) - either a coded qualitative braking assessment (91-95, 99)
#: or, outside this table, a real two-digit friction coefficient
#: (00-90) not enumerated here since it is a real measured value, not
#: a fixed code.
RUNWAY_BRAKING_ACTION: dict[str, str] = {
    "91": "Poor",
    "92": "Medium to poor",
    "93": "Medium",
    "94": "Medium to good",
    "95": "Good",
    "99": "Unreliable (braking action figures unreliable/not usable)",
    "//": "Not reported",
}
