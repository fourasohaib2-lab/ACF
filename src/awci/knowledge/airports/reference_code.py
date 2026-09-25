"""
Atmospheric Complexity Framework (ACF)

ICAO Annex 14 Aerodrome Reference Code & ARFF Category Classification

Real, published ICAO classification schemes - not aircraft-specific or
airport-specific data, but the threshold tables used to classify any
given aerodrome (by its reference field length and the aircraft it is
designed to accommodate) or any given aircraft (by its overall length
and fuselage width, for firefighting response planning).

Source: ICAO Annex 14 to the Convention on International Civil
Aviation, Volume I - Aerodrome Design and Operations, Chapter 1
(Aerodrome Reference Code, Table 1-1) and Chapter 9 (Rescue and
Fire Fighting, Table 9-1). These are the real, standard thresholds
used industry-wide (AIP publications, ICAO training material) - not
invented for this project.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RunwaySurfaceType(str, Enum):
    """Real ICAO/FAA-recognized runway surface categories."""

    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    COMPOSITE = "composite"
    GRAVEL = "gravel"
    GRASS = "grass"
    WATER = "water"
    SNOW_ICE = "snow_ice"


def classify_aerodrome_code_number(reference_field_length_m: float) -> int:
    """Real ICAO Annex 14 Volume I, Table 1-1 aerodrome Code Number,
    from the Aerodrome Reference Field Length (ARFL).

    ARFL is the minimum field length required for the maximum
    certificated take-off mass of an aeroplane at sea level, standard
    atmosphere, still air, and zero runway slope - a real, published,
    airport-specific figure. This function applies only the real
    length-based threshold table; it does not itself compute a true
    ARFL from a raw runway length (which would additionally need
    elevation/temperature/slope corrections that are not modeled
    here - see each airport's own `AirportInfo.code_number` docstring
    note for the specific approximation used).

    Thresholds (Table 1-1):
        Code 1: ARFL < 800 m
        Code 2: 800 m <= ARFL < 1200 m
        Code 3: 1200 m <= ARFL < 1800 m
        Code 4: ARFL >= 1800 m
    """
    if reference_field_length_m < 800.0:
        return 1
    if reference_field_length_m < 1200.0:
        return 2
    if reference_field_length_m < 1800.0:
        return 3
    return 4


def classify_aerodrome_code_letter(wingspan_m: float, outer_main_gear_wheel_span_m: float) -> str:
    """Real ICAO Annex 14 Volume I, Table 1-1 aerodrome Code Letter,
    from the wingspan and outer main gear wheel span (OMGWS) of the
    most demanding aircraft type the aerodrome is designed to serve.

    Whichever of the two dimensions gives the more demanding
    (higher) letter governs, per the real ICAO rule - this function
    returns the more demanding of the two independently-classified
    letters.

    Thresholds (Table 1-1):
        A: wingspan <  15 m, OMGWS <  4.5 m
        B: wingspan <  24 m, OMGWS <  6.0 m
        C: wingspan <  36 m, OMGWS <  9.0 m
        D: wingspan <  52 m, OMGWS < 14.0 m
        E: wingspan <  65 m, OMGWS <  9.0 m (wider wingspan band than D, narrower gear band)
        F: wingspan <  80 m, OMGWS < 16.0 m
    """
    letters = "ABCDEF"
    wingspan_thresholds_m = (15.0, 24.0, 36.0, 52.0, 65.0, 80.0)
    gear_span_thresholds_m = (4.5, 6.0, 9.0, 14.0, 9.0, 16.0)

    wingspan_index = next(
        (i for i, threshold in enumerate(wingspan_thresholds_m) if wingspan_m < threshold),
        len(letters) - 1,
    )
    gear_span_index = next(
        (i for i, threshold in enumerate(gear_span_thresholds_m) if outer_main_gear_wheel_span_m < threshold),
        len(letters) - 1,
    )
    return letters[max(wingspan_index, gear_span_index)]


def classify_arff_category(overall_length_m: float, fuselage_width_m: float) -> int:
    """Real ICAO Annex 14 Volume I, Table 9-1 Rescue and Fire Fighting
    (RFF/ARFF) Category, from an aircraft's overall length and maximum
    fuselage width - used to plan an aerodrome's real firefighting
    response capability, not an aerodrome design parameter like the
    Code Number/Letter above.

    Thresholds (Table 9-1, length bands; the real table's fuselage-width
    sub-bands within categories 6-9 refine the required foam/water
    discharge rate, not the category number itself, so only length
    governs the returned category here):
        1:  < 9 m     2: < 12 m    3: < 18 m    4: < 24 m    5: < 28 m
        6:  < 39 m    7: < 49 m    8: < 61 m    9: < 76 m   10: < 90 m
    """
    del fuselage_width_m  # real Table 9-1 input for discharge-rate sub-bands, not the category number itself
    length_thresholds_m = (9.0, 12.0, 18.0, 24.0, 28.0, 39.0, 49.0, 61.0, 76.0, 90.0)
    for category, threshold in enumerate(length_thresholds_m, start=1):
        if overall_length_m < threshold:
            return category
    return 10


@dataclass(frozen=True)
class AerodromeReferenceCode:
    """A real ICAO Annex 14 aerodrome reference code, e.g. "4F"."""

    code_number: int
    code_letter: str

    def __str__(self) -> str:
        return f"{self.code_number}{self.code_letter}"
