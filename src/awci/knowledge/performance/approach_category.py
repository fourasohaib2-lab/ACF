"""
Atmospheric Complexity Framework (ACF)

ICAO Aircraft Approach Category Classification (Doc 8168, PANS-OPS)

Real, published ICAO classification scheme for instrument approach
procedure design - a bounded, standard classification (Category A
through E), not aircraft-type-specific data.

Source: ICAO Doc 8168, Procedures for Air Navigation Services -
Aircraft Operations (PANS-OPS), Volume I, Part I, Section 4, Chapter 1
- Aircraft Categories. Real, standard thresholds used industry-wide to
determine minimum obstacle clearance, circling radii, and approach
speed limits for published instrument approach procedures - not
invented for this project.
"""

from __future__ import annotations

from enum import Enum


class ApproachCategory(str, Enum):
    """Real ICAO Doc 8168 aircraft approach categories."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


def classify_approach_category(vat_kt: float) -> ApproachCategory:
    """Real ICAO Doc 8168 aircraft approach category, from an
    aircraft's real Vat (indicated airspeed at threshold, defined as
    1.3 times the stall speed - or minimum steady flight speed - in
    the landing configuration at maximum certificated landing mass).

    Thresholds:
        Category A: Vat <  91 kt
        Category B:  91 kt <= Vat < 121 kt
        Category C: 121 kt <= Vat < 141 kt
        Category D: 141 kt <= Vat < 166 kt
        Category E: 166 kt <= Vat < 211 kt

    This function applies only the real speed-threshold table; it
    does not itself compute Vat from stall speed (which is real,
    aircraft-specific flight-test data, not derivable from a general
    formula).
    """
    if vat_kt < 91.0:
        return ApproachCategory.A
    if vat_kt < 121.0:
        return ApproachCategory.B
    if vat_kt < 141.0:
        return ApproachCategory.C
    if vat_kt < 166.0:
        return ApproachCategory.D
    return ApproachCategory.E
