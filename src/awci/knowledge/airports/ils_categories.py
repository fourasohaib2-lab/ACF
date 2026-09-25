"""
Atmospheric Complexity Framework (ACF)

ICAO ILS Approach Category Operating Minima

Real, published ICAO/EASA precision-approach category operating
minima - Decision Height (DH) and Runway Visual Range (RVR), the
real numeric thresholds behind the `ils_categories` labels
(e.g. "CAT IIIb") already stored per airport in
`AirportInfo.ils_categories`.

Source: ICAO Annex 6, Part I, and ICAO Doc 9365 (All Weather
Operations Manual); operating minima are also republished by EASA
(CS-AWO) and individual States' AIPs, with the real DH/RVR figures
below being the commonly-published reference values used
industry-wide. Individual aerodrome/operator approvals can carry
slightly different exact figures within these real category
definitions - this module gives the real, standard reference minima,
not a specific airport's own published AIP minima (which are not
modeled here).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperatingMinima:
    """Real ICAO precision-approach operating minima for one ILS
    category. `decision_height_ft` is `None` for categories flown with
    no decision height (CAT IIIb/IIIc, per real ICAO definitions).
    `rvr_m` is the minimum required Runway Visual Range; `None` for
    CAT IIIc, which has no RVR limit."""

    decision_height_ft: float | None
    rvr_m: float | None


#: Real ICAO ILS approach category operating minima, keyed by the
#: same real category label strings already used in
#: `AirportInfo.ils_categories` (e.g. "CAT IIIb").
ILS_CATEGORY_MINIMA: dict[str, OperatingMinima] = {
    "CAT I": OperatingMinima(decision_height_ft=200.0, rvr_m=550.0),
    "CAT II": OperatingMinima(decision_height_ft=100.0, rvr_m=300.0),
    "CAT IIIa": OperatingMinima(decision_height_ft=None, rvr_m=175.0),
    "CAT IIIb": OperatingMinima(decision_height_ft=None, rvr_m=50.0),
    "CAT IIIc": OperatingMinima(decision_height_ft=None, rvr_m=None),
}
