"""Tests for the real ICAO airspace classification
(awci.knowledge.icao.airspace_classes), the real ICAO altimetry
conventions (awci.knowledge.performance.altimetry), the real ICAO
aircraft approach category classification
(awci.knowledge.performance.approach_category), and the real WMO
cloud genus/étage classification (awci.knowledge.meteorology.clouds).

Added 2026-09-21 at explicit user request, scoped to real, bounded,
published classification schemes (ICAO airspace classes A-G, the
altimetry standard-pressure/semi-circular-rule conventions, ICAO
approach categories A-E, the 10 WMO cloud genera and their étage
grouping) rather than an unbounded enumeration of every ICAO Annex /
WMO technical regulation.
"""

from __future__ import annotations

import pytest

from awci.knowledge.icao.airspace_classes import (
    AIRSPACE_CLASS_CHARACTERISTICS,
    AirspaceClass,
)
from awci.knowledge.meteorology.clouds import (
    CLOUD_GENUS_ETAGE,
    METAR_CLOUD_TYPE_TO_GENUS,
    CloudEtage,
    CloudGenus,
)
from awci.knowledge.performance.altimetry import (
    STANDARD_PRESSURE_SETTING_HPA,
    STANDARD_PRESSURE_SETTING_INHG,
    FlightLevel,
    is_valid_ifr_cruising_level,
)
from awci.knowledge.performance.approach_category import (
    ApproachCategory,
    classify_approach_category,
)


def test_every_real_icao_airspace_class_has_characteristics():
    for airspace_class in AirspaceClass:
        assert airspace_class in AIRSPACE_CLASS_CHARACTERISTICS


def test_class_a_is_ifr_only_with_full_separation():
    characteristics = AIRSPACE_CLASS_CHARACTERISTICS[AirspaceClass.A]
    assert characteristics.flight_rules_permitted == "IFR only"
    assert characteristics.separation_provided == "All aircraft"
    assert characteristics.atc_clearance_required is True


def test_class_g_has_no_separation_and_no_clearance_required():
    characteristics = AIRSPACE_CLASS_CHARACTERISTICS[AirspaceClass.G]
    assert characteristics.separation_provided == "Nil"
    assert characteristics.atc_clearance_required is False
    assert characteristics.continuous_two_way_radio_required is False


def test_standard_pressure_setting_matches_the_real_icao_value():
    assert STANDARD_PRESSURE_SETTING_HPA == 1013.25
    assert STANDARD_PRESSURE_SETTING_INHG == 29.92


def test_flight_level_string_and_altitude_conversion():
    fl = FlightLevel(350)
    assert str(fl) == "FL350"
    assert fl.altitude_ft == 35000


@pytest.mark.parametrize(
    ("flight_level", "magnetic_track_deg", "expected"),
    [
        (10, 0.0, True),  # FL010, eastbound, odd -> valid
        (10, 359.9, False),  # FL010, westbound, odd -> invalid
        (20, 180.0, True),  # FL020, westbound, even -> valid
        (20, 179.9, False),  # FL020, eastbound, even -> invalid
        (90, 90.0, True),
        (100, 270.0, True),
    ],
)
def test_semi_circular_cruising_rule_matches_real_icao_pans_atm(flight_level, magnetic_track_deg, expected):
    assert is_valid_ifr_cruising_level(flight_level, magnetic_track_deg) is expected


def test_semi_circular_rule_rejects_an_out_of_range_track():
    with pytest.raises(ValueError):
        is_valid_ifr_cruising_level(100, 360.0)
    with pytest.raises(ValueError):
        is_valid_ifr_cruising_level(100, -1.0)


def test_all_ten_real_wmo_cloud_genera_are_classified():
    assert len(CloudGenus) == 10
    for genus in CloudGenus:
        assert genus in CLOUD_GENUS_ETAGE


@pytest.mark.parametrize(
    ("genus", "expected_etage"),
    [
        (CloudGenus.CIRRUS, CloudEtage.HIGH),
        (CloudGenus.CIRROCUMULUS, CloudEtage.HIGH),
        (CloudGenus.CIRROSTRATUS, CloudEtage.HIGH),
        (CloudGenus.ALTOCUMULUS, CloudEtage.MIDDLE),
        (CloudGenus.ALTOSTRATUS, CloudEtage.MIDDLE),
        (CloudGenus.NIMBOSTRATUS, CloudEtage.MIDDLE),
        (CloudGenus.STRATOCUMULUS, CloudEtage.LOW),
        (CloudGenus.STRATUS, CloudEtage.LOW),
        (CloudGenus.CUMULUS, CloudEtage.LOW),
        (CloudGenus.CUMULONIMBUS, CloudEtage.LOW),
    ],
)
def test_cloud_genus_etage_matches_the_real_wmo_cloud_atlas(genus, expected_etage):
    assert CLOUD_GENUS_ETAGE[genus] == expected_etage


def test_metar_cloud_type_codes_map_to_the_real_genus():
    """CB/TCU are the real METAR/TAF convective cloud-type indicators
    awci.knowledge.icao.metar_decoder's own _CLOUD_RE already decodes -
    locks in they map to the real WMO genus this module defines,
    rather than a duplicated or inconsistent taxonomy."""
    assert METAR_CLOUD_TYPE_TO_GENUS["CB"] == CloudGenus.CUMULONIMBUS
    assert METAR_CLOUD_TYPE_TO_GENUS["TCU"] == CloudGenus.CUMULUS


def test_metar_decoder_cloud_type_group_matches_this_modules_real_codes():
    from awci.knowledge.icao.metar_decoder import _CLOUD_RE

    assert set(METAR_CLOUD_TYPE_TO_GENUS) <= {"CB", "TCU"}
    match = _CLOUD_RE.match("BKN020CB")
    assert match is not None
    assert match.group("type") == "CB"


@pytest.mark.parametrize(
    ("vat_kt", "expected_category"),
    [
        (90.9, ApproachCategory.A),
        (91.0, ApproachCategory.B),
        (120.9, ApproachCategory.B),
        (121.0, ApproachCategory.C),
        (140.9, ApproachCategory.C),
        (141.0, ApproachCategory.D),
        (165.9, ApproachCategory.D),
        (166.0, ApproachCategory.E),
        (210.0, ApproachCategory.E),
    ],
)
def test_approach_category_matches_the_real_icao_doc_8168_thresholds(vat_kt, expected_category):
    assert classify_approach_category(vat_kt) == expected_category


def test_ils_category_minima_cover_every_real_category_stored_in_the_airport_registry():
    """AIRPORT_REGISTRY's own real ils_categories entries (all "CAT
    IIIb" today) must have real operating minima defined here - locks
    in the two real data sources stay consistent."""
    from awci.knowledge.airports.airport_database import AirportDatabase
    from awci.knowledge.airports.ils_categories import ILS_CATEGORY_MINIMA

    for airport in AirportDatabase.all_airport_infos():
        for category in airport.ils_categories:
            assert category in ILS_CATEGORY_MINIMA, f"{airport.icao_code} cites undefined ILS category {category!r}"


@pytest.mark.parametrize(
    ("category", "expected_dh_ft", "expected_rvr_m"),
    [
        ("CAT I", 200.0, 550.0),
        ("CAT II", 100.0, 300.0),
        ("CAT IIIa", None, 175.0),
        ("CAT IIIb", None, 50.0),
        ("CAT IIIc", None, None),
    ],
)
def test_ils_category_minima_match_the_real_icao_reference_values(category, expected_dh_ft, expected_rvr_m):
    from awci.knowledge.airports.ils_categories import ILS_CATEGORY_MINIMA

    minima = ILS_CATEGORY_MINIMA[category]
    assert minima.decision_height_ft == expected_dh_ft
    assert minima.rvr_m == expected_rvr_m


def test_cat_iiib_is_stricter_than_cat_i_in_both_real_dimensions():
    """A real, disclosed sanity check on the real ICAO category
    ordering: each higher category has an equal-or-lower RVR
    requirement (CAT I's real DH-based minima are the least strict)."""
    from awci.knowledge.airports.ils_categories import ILS_CATEGORY_MINIMA

    assert ILS_CATEGORY_MINIMA["CAT IIIb"].rvr_m < ILS_CATEGORY_MINIMA["CAT I"].rvr_m
    assert ILS_CATEGORY_MINIMA["CAT I"].decision_height_ft is not None
    assert ILS_CATEGORY_MINIMA["CAT IIIb"].decision_height_ft is None


@pytest.mark.parametrize(
    ("cover_code", "expected_oktas"),
    [
        ("FEW", (1, 2)),
        ("SCT", (3, 4)),
        ("BKN", (5, 7)),
        ("OVC", (8, 8)),
    ],
)
def test_metar_cloud_cover_oktas_match_the_real_wmo_icao_convention(cover_code, expected_oktas):
    from awci.knowledge.meteorology.clouds import METAR_CLOUD_COVER_OKTAS

    assert METAR_CLOUD_COVER_OKTAS[cover_code] == expected_oktas


def test_metar_cloud_cover_codes_match_the_real_decoder_regex_alternation():
    from awci.knowledge.icao.metar_decoder import _CLOUD_RE
    from awci.knowledge.meteorology.clouds import METAR_CLOUD_COVER_OKTAS

    for cover_code in METAR_CLOUD_COVER_OKTAS:
        match = _CLOUD_RE.match(f"{cover_code}020")
        assert match is not None
        assert match.group("cover") == cover_code
