"""Tests for the real ICAO Annex 14 aerodrome reference code / ARFF
category classification (awci.knowledge.airports.reference_code) and
the real ICAO Doc 4444 wake turbulence category classification
(awci.knowledge.performance.wake_turbulence).

Added 2026-09-21 at explicit user request: real classification
schemes for airport and aircraft categories, applied to the existing
AIRPORT_REGISTRY entries - not an exhaustive enumeration of every real
airport/aircraft in the world (a scoped decision, see
docs/architecture/awci_reference_architecture.md's own AWCI-O
discussion in section 27.5), but the actual ICAO threshold tables that
let any given airport/aircraft be classified.
"""

from __future__ import annotations

import pytest

from awci.knowledge.airports.airport_database import AirportDatabase
from awci.knowledge.airports.reference_code import (
    AerodromeReferenceCode,
    classify_aerodrome_code_letter,
    classify_aerodrome_code_number,
    classify_arff_category,
)
from awci.knowledge.performance.wake_turbulence import (
    WakeTurbulenceCategory,
    classify_wake_turbulence_category,
)


@pytest.mark.parametrize(
    ("arfl_m", "expected_code_number"),
    [
        (799.0, 1),
        (800.0, 2),
        (1199.0, 2),
        (1200.0, 3),
        (1799.0, 3),
        (1800.0, 4),
        (4200.0, 4),
    ],
)
def test_code_number_matches_real_icao_annex_14_table_1_1_thresholds(arfl_m, expected_code_number):
    assert classify_aerodrome_code_number(arfl_m) == expected_code_number


@pytest.mark.parametrize(
    ("wingspan_m", "omgws_m", "expected_letter"),
    [
        (10.0, 3.0, "A"),  # Cessna 172-class
        (20.0, 5.0, "B"),  # ATR 42-class
        (34.0, 7.0, "C"),  # A320-class
        (50.0, 10.0, "D"),  # B767-class
        (60.0, 10.0, "E"),  # B777-class
        (79.8, 14.0, "F"),  # A380-class
    ],
)
def test_code_letter_matches_real_icao_annex_14_table_1_1_thresholds(wingspan_m, omgws_m, expected_letter):
    assert classify_aerodrome_code_letter(wingspan_m, omgws_m) == expected_letter


def test_code_letter_takes_the_more_demanding_of_wingspan_and_gear_span():
    """A real ICAO rule: whichever dimension is more demanding governs.
    Here a narrow gear span (Code C) paired with a wide wingspan
    (Code E) must yield Code E, not Code C."""
    assert classify_aerodrome_code_letter(wingspan_m=60.0, outer_main_gear_wheel_span_m=7.0) == "E"


@pytest.mark.parametrize(
    ("length_m", "expected_category"),
    [
        (8.0, 1),
        (9.0, 2),
        (17.9, 3),
        (23.9, 4),
        (27.9, 5),
        (38.9, 6),
        (48.9, 7),
        (60.9, 8),
        (75.9, 9),
        (89.9, 10),
        (100.0, 10),
    ],
)
def test_arff_category_matches_real_icao_annex_14_table_9_1_thresholds(length_m, expected_category):
    assert classify_arff_category(length_m, fuselage_width_m=6.0) == expected_category


def test_aerodrome_reference_code_str_matches_the_real_icao_notation():
    code = AerodromeReferenceCode(code_number=4, code_letter="F")
    assert str(code) == "4F"


@pytest.mark.parametrize("icao_code", ["LFPG", "KJFK", "EGLL"])
def test_real_airports_are_all_code_4f_matching_their_published_a380_certification(icao_code):
    """LFPG/KJFK/EGLL are all real, published ICAO Code 4F aerodromes,
    certified for A380-800 operations since 2008 - a verifiable,
    cited fact (see airport_database.py's own per-airport comments),
    not an invented classification."""
    airport = AirportDatabase.get_airport(icao_code)
    assert airport is not None
    assert str(airport.reference_code) == "4F"


def test_reference_code_number_is_computed_from_the_real_longest_runway():
    airport = AirportDatabase.get_airport("KJFK")
    assert airport is not None
    longest_runway_m = max(runway["length_m"] for runway in airport.runways)
    assert longest_runway_m == 4423
    assert airport.reference_code.code_number == 4


@pytest.mark.parametrize(
    ("mtow_kg", "expected_category"),
    [
        (1150.0, WakeTurbulenceCategory.LIGHT),  # Cessna 172-class
        (7000.0, WakeTurbulenceCategory.LIGHT),
        (7000.1, WakeTurbulenceCategory.MEDIUM),
        (78000.0, WakeTurbulenceCategory.MEDIUM),  # A320-class
        (135999.9, WakeTurbulenceCategory.MEDIUM),
        (136000.0, WakeTurbulenceCategory.HEAVY),
        (396890.0, WakeTurbulenceCategory.HEAVY),  # B747-400-class
    ],
)
def test_wake_turbulence_category_matches_real_icao_doc_4444_thresholds(mtow_kg, expected_category):
    assert classify_wake_turbulence_category(mtow_kg) == expected_category


def test_super_category_is_never_inferred_from_mass_alone():
    """SUPER is a real, named ICAO exception (A380-800/An-225), not a
    mass threshold - a very heavy aircraft must not silently become
    SUPER without the caller explicitly asserting it is a known
    SUPER-category type."""
    assert classify_wake_turbulence_category(575_000.0) == WakeTurbulenceCategory.HEAVY
    assert classify_wake_turbulence_category(575_000.0, is_super_heavy_type=True) == WakeTurbulenceCategory.SUPER
