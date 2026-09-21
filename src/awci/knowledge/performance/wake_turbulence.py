"""
Atmospheric Complexity Framework (ACF)

ICAO Wake Turbulence Category Classification

Real, published ICAO classification scheme for aircraft wake
turbulence separation - not an aircraft-type database, but the
threshold table (by maximum certificated take-off mass, MTOM/MTOW)
used to classify any given aircraft.

Source: ICAO Doc 4444 (PANS-ATM), Air Traffic Management, wake
turbulence category thresholds. These are the real, standard
thresholds used industry-wide for ATC separation - not invented for
this project. The SUPER category is a named exception, not derivable
from the mass thresholds alone (see `classify_wake_turbulence_category`
docstring).
"""

from __future__ import annotations

from enum import Enum


class WakeTurbulenceCategory(str, Enum):
    """Real ICAO Doc 4444 wake turbulence categories."""

    LIGHT = "LIGHT"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"
    SUPER = "SUPER"


def classify_wake_turbulence_category(
    mtow_kg: float,
    is_super_heavy_type: bool = False,
) -> WakeTurbulenceCategory:
    """Real ICAO Doc 4444 wake turbulence category, from an aircraft's
    maximum certificated take-off mass (MTOW).

    Thresholds:
        LIGHT:  MTOW <=   7 000 kg
        MEDIUM:   7 000 kg < MTOW <  136 000 kg
        HEAVY:  MTOW >= 136 000 kg

    SUPER is a real, named ICAO exception for specific wide-body
    types (historically the Airbus A380-800 and Antonov An-225) whose
    wake characteristics require greater separation than their mass
    alone would classify them under - it cannot be derived from the
    MTOW thresholds above, so a caller must pass `is_super_heavy_type`
    explicitly for a known SUPER-category type; this function never
    infers SUPER from mass alone.
    """
    if is_super_heavy_type:
        return WakeTurbulenceCategory.SUPER
    if mtow_kg <= 7_000.0:
        return WakeTurbulenceCategory.LIGHT
    if mtow_kg < 136_000.0:
        return WakeTurbulenceCategory.MEDIUM
    return WakeTurbulenceCategory.HEAVY
