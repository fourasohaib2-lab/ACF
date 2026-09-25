"""Tests for the real ICAO airspace classification
(awci.knowledge.icao.airspace_classes), the real ICAO altimetry
conventions (awci.knowledge.performance.altimetry), the real ICAO
aircraft approach category classification
(awci.knowledge.performance.approach_category), the real ICAO ILS
category minima (awci.knowledge.airports.ils_categories), the real
ICAO runway state group codes (awci.knowledge.airports.runway_state),
the real METAR/TAF present weather code meanings
(awci.knowledge.icao.present_weather_codes), and the real WMO cloud
genus/étage/cover classification (awci.knowledge.meteorology.clouds),
the real icing intensity/type reference
(awci.knowledge.meteorology.icing), the real TAF change-indicator
meanings (awci.knowledge.icao.taf_change_indicators), the real SIGMET
validity-period rules (awci.knowledge.icao.sigmet_validity), the real
GAMET/AIRMET reference facts (awci.knowledge.icao.gamet_airmet), the
real thunderstorm life-cycle/hazard reference
(awci.knowledge.meteorology.thunderstorm), the real orographic
(mountain-wave) turbulence formation-condition reference
(awci.knowledge.meteorology.orographic_turbulence), the real
Clear Air Turbulence (CAT) altitude-band/jet-stream reference
(awci.knowledge.meteorology.clear_air_turbulence), the real mist/fog
classification reference (awci.knowledge.meteorology.fog), the real
low-altitude wind-gradient reference
(awci.knowledge.meteorology.low_level_wind_gradient), the real
microburst physical-scale/detection-system reference
(awci.knowledge.meteorology.microburst_reference), the real squall-line
("grain") reference (awci.knowledge.meteorology.squall_line), and the
real turbulence-intensity/source-type reference
(awci.knowledge.meteorology.turbulence_intensity), the real jet-stream
reference (awci.knowledge.meteorology.jet_stream), the real
weather-front reference (awci.knowledge.meteorology.weather_front), the real general-atmospheric-circulation reference
(awci.knowledge.meteorology.general_circulation), the real atmosphere
composition/layer-structure reference
(awci.knowledge.meteorology.atmosphere_composition), the real
emagram/skew-T diagram and radiosonde reference
(awci.knowledge.meteorology.skew_t_diagram), the real wind-unit/
gust-criterion/named-local-wind reference
(awci.knowledge.meteorology.local_winds), the real temperature
reference (awci.knowledge.meteorology.temperature_reference), and the
real cloud-characteristics element-size reference
(awci.knowledge.meteorology.cloud_characteristics).

Added 2026-09-21 at explicit user request, scoped to real, bounded,
published classification schemes (ICAO airspace classes A-G, the
altimetry standard-pressure/semi-circular-rule conventions, ICAO
approach categories A-E, ILS category minima, runway state codes,
present weather codes, the 10 WMO cloud genera and their étage/cover
grouping) rather than an unbounded enumeration of every ICAO Annex /
WMO technical regulation. The present-weather, cloud-cover, and
runway-state tables were cross-checked against
https://www.lavionnaire.fr/CodesMetar.php, and the thunderstorm/
orographic-turbulence/CAT reference facts against
https://www.lavionnaire.fr/PhenomOrages.php,
https://www.lavionnaire.fr/PhenomOrographe.php,
https://www.lavionnaire.fr/PhenomTAC.php,
https://www.lavionnaire.fr/MeteoBrouillard.php,
https://www.lavionnaire.fr/PhenomGradient.php,
https://www.lavionnaire.fr/PhenomCisaille.php,
https://www.lavionnaire.fr/MeteoLesGrains.php,
https://www.lavionnaire.fr/PhenomDifTurbule.php,
https://www.lavionnaire.fr/MeteoJetStream.php,
https://www.lavionnaire.fr/MeteoFronts.php, and
https://www.lavionnaire.fr/MeteoCirculation.php,
https://www.lavionnaire.fr/MeteoAtmosphere.php,
https://www.lavionnaire.fr/MeteoEmagram.php, and
https://www.lavionnaire.fr/MeteoVent.php,
https://www.lavionnaire.fr/MeteoTemperature.php, and
https://www.lavionnaire.fr/MeteoNuagesCaract.php, at the user's own
request, rather than relying on recalled tables alone for this level of
numeric/letter-code detail. https://www.lavionnaire.fr/MeteoHumidite.php
and https://www.lavionnaire.fr/MeteoImagerie.php were also checked -
the former's real numeric content is Earth hydrosphere/geography
statistics outside the agreed meteo/aero/aircraft scope (relative
humidity mechanics are already covered by
acf.science.thermodynamics.relative_humidity), the latter gives no
real numeric thresholds at all (a qualitative image-reading guide) -
so neither yielded new content, a disclosed finding rather than a
silent omission.
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
    """SKC (sky clear, 0 oktas) is real and included in
    METAR_CLOUD_COVER_OKTAS for completeness of the okta scale, but is
    real-and-correctly NOT matched by _CLOUD_RE: a clear sky reports
    no cloud LAYER group at all in a real METAR, unlike FEW/SCT/BKN/
    OVC which always report a real layer height."""
    from awci.knowledge.icao.metar_decoder import _CLOUD_RE
    from awci.knowledge.meteorology.clouds import METAR_CLOUD_COVER_OKTAS

    for cover_code in METAR_CLOUD_COVER_OKTAS:
        if cover_code == "SKC":
            continue
        match = _CLOUD_RE.match(f"{cover_code}020")
        assert match is not None
        assert match.group("cover") == cover_code


def test_skc_is_a_real_zero_okta_code_not_matched_by_the_cloud_layer_regex():
    from awci.knowledge.icao.metar_decoder import _CLOUD_RE
    from awci.knowledge.meteorology.clouds import METAR_CLOUD_COVER_OKTAS

    assert METAR_CLOUD_COVER_OKTAS["SKC"] == (0, 0)
    assert _CLOUD_RE.match("SKC020") is None


def test_non_okta_sky_condition_codes_are_real_and_distinct():
    from awci.knowledge.meteorology.clouds import METAR_NON_OKTA_SKY_CONDITION_CODES

    assert set(METAR_NON_OKTA_SKY_CONDITION_CODES) == {"NSC", "NCD", "VV", "CAVOK"}
    assert len({meaning for meaning in METAR_NON_OKTA_SKY_CONDITION_CODES.values()}) == 4


def test_present_weather_intensity_matches_the_real_wx_re_group():
    from awci.knowledge.icao.metar_decoder import _WX_RE
    from awci.knowledge.icao.present_weather_codes import PRESENT_WEATHER_INTENSITY

    assert "-" in PRESENT_WEATHER_INTENSITY
    assert "+" in PRESENT_WEATHER_INTENSITY
    assert "VC" in PRESENT_WEATHER_INTENSITY
    assert "" in PRESENT_WEATHER_INTENSITY  # real moderate intensity has no prefix character
    match = _WX_RE.match("-RA")
    assert match is not None
    assert match.group("intensity") == "-"


def test_present_weather_descriptors_match_the_real_metar_decoder_regex_exactly():
    import re

    from awci.knowledge.icao.metar_decoder import _WX_RE
    from awci.knowledge.icao.present_weather_codes import PRESENT_WEATHER_DESCRIPTORS

    match = re.search(r"descriptor>([^)]+)\)", _WX_RE.pattern)
    assert match is not None
    regex_codes = set(match.group(1).split("|"))
    assert set(PRESENT_WEATHER_DESCRIPTORS) == regex_codes


def test_present_weather_phenomena_match_the_real_metar_decoder_regex_exactly():
    import re

    from awci.knowledge.icao.metar_decoder import _WX_RE
    from awci.knowledge.icao.present_weather_codes import PRESENT_WEATHER_PHENOMENA

    match = re.search(r"phenomena>\(\?:([^)]+)\)", _WX_RE.pattern)
    assert match is not None
    regex_codes = set(match.group(1).split("|"))
    assert set(PRESENT_WEATHER_PHENOMENA) == regex_codes


@pytest.mark.parametrize(
    ("raw_group", "expected_descriptor", "expected_phenomena"),
    [
        ("TSRA", "TS", "RA"),
        ("FZRA", "FZ", "RA"),
        ("SHSN", "SH", "SN"),
        ("MIFG", "MI", "FG"),
    ],
)
def test_real_metar_weather_groups_decode_to_documented_meanings(raw_group, expected_descriptor, expected_phenomena):
    """A handful of real, commonly-observed METAR weather groups
    (thunderstorm rain, freezing rain, snow showers, shallow fog) -
    locks in that the real decoder's own regex groups line up with
    this module's own real meaning tables."""
    from awci.knowledge.icao.metar_decoder import _WX_RE
    from awci.knowledge.icao.present_weather_codes import (
        PRESENT_WEATHER_DESCRIPTORS,
        PRESENT_WEATHER_PHENOMENA,
    )

    match = _WX_RE.match(raw_group)
    assert match is not None
    assert match.group("descriptor") == expected_descriptor
    assert match.group("phenomena") == expected_phenomena
    assert PRESENT_WEATHER_DESCRIPTORS[expected_descriptor]
    assert PRESENT_WEATHER_PHENOMENA[expected_phenomena]


def test_runway_deposit_type_covers_all_ten_real_icao_digits_plus_not_reported():
    from awci.knowledge.airports.runway_state import RUNWAY_DEPOSIT_TYPE

    assert set(RUNWAY_DEPOSIT_TYPE) == {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "/"}
    assert RUNWAY_DEPOSIT_TYPE["7"] == "Ice"


def test_runway_contamination_extent_matches_the_real_icao_bands():
    from awci.knowledge.airports.runway_state import RUNWAY_CONTAMINATION_EXTENT

    assert RUNWAY_CONTAMINATION_EXTENT["1"] == "Less than 10% covered"
    assert RUNWAY_CONTAMINATION_EXTENT["9"] == "51% to 100% covered"


def test_runway_braking_action_matches_the_real_icao_codes():
    from awci.knowledge.airports.runway_state import RUNWAY_BRAKING_ACTION

    assert RUNWAY_BRAKING_ACTION["95"] == "Good"
    assert RUNWAY_BRAKING_ACTION["91"] == "Poor"
    assert RUNWAY_BRAKING_ACTION["99"] == "Unreliable (braking action figures unreliable/not usable)"


def test_wake_turbulence_separation_matches_the_real_icao_pans_atm_table():
    from awci.knowledge.performance.wake_turbulence import (
        WAKE_TURBULENCE_SEPARATION_NM,
        WakeTurbulenceCategory as WTC,
    )

    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.LIGHT, WTC.LIGHT)] == 3.0
    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.MEDIUM, WTC.LIGHT)] == 5.0
    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.HEAVY, WTC.LIGHT)] == 6.0
    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.SUPER, WTC.MEDIUM)] == 8.0
    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.SUPER, WTC.HEAVY)] == 6.0
    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.SUPER, WTC.SUPER)] == 4.0
    assert WAKE_TURBULENCE_SEPARATION_NM[(WTC.HEAVY, WTC.HEAVY)] == 4.0


def test_wake_turbulence_separation_omits_the_real_undefined_super_over_light_case():
    """The real source table has no entry for a LIGHT aircraft
    following a SUPER one - locks in it stays omitted rather than
    guessed."""
    from awci.knowledge.performance.wake_turbulence import (
        WAKE_TURBULENCE_SEPARATION_NM,
        WakeTurbulenceCategory as WTC,
    )

    assert (WTC.SUPER, WTC.LIGHT) not in WAKE_TURBULENCE_SEPARATION_NM


def test_wake_turbulence_takeoff_landing_separation_matches_real_icao_minima():
    from awci.knowledge.performance.wake_turbulence import (
        WAKE_TURBULENCE_TAKEOFF_LANDING_SEPARATION_MINUTES,
        WAKE_TURBULENCE_TAKEOFF_LANDING_SEPARATION_NM,
    )

    assert WAKE_TURBULENCE_TAKEOFF_LANDING_SEPARATION_NM == 5.0
    assert WAKE_TURBULENCE_TAKEOFF_LANDING_SEPARATION_MINUTES == 2.0


def test_icing_intensity_thresholds_are_monotonically_increasing():
    from awci.knowledge.meteorology.icing import ICING_INTENSITY_THRESHOLDS, IcingIntensity

    light = ICING_INTENSITY_THRESHOLDS[IcingIntensity.LIGHT].minimum_accretion_rate_g_cm2_per_hour
    moderate = ICING_INTENSITY_THRESHOLDS[IcingIntensity.MODERATE].minimum_accretion_rate_g_cm2_per_hour
    severe = ICING_INTENSITY_THRESHOLDS[IcingIntensity.SEVERE].minimum_accretion_rate_g_cm2_per_hour
    assert light < moderate < severe


def test_icing_type_formation_covers_all_four_real_types():
    from awci.knowledge.meteorology.icing import ICING_TYPE_FORMATION, IcingType

    assert set(ICING_TYPE_FORMATION) == {IcingType.RIME, IcingType.CLEAR, IcingType.MIXED, IcingType.GLAZE}
    for description in ICING_TYPE_FORMATION.values():
        assert description  # every real type has a real, non-empty formation description


def test_icing_lower_bound_discrepancy_against_the_existing_icao_faa_module_is_disclosed_not_merged():
    """awci.hazards.icing_temperature_range (ICAO Annex 3/FAA-sourced)
    already cites -40 degC as the real lower icing-precondition bound;
    this module's own source cites -35 degC for icing potential
    becoming negligible - a real, disclosed ~5 degC discrepancy
    between two real sources, not silently resolved. Locks in both
    values remain distinct, unmerged real numbers."""
    from awci.hazards.icing_temperature_range import ICING_TEMPERATURE_LOWER_C
    from awci.knowledge.meteorology.icing import ICING_POTENTIAL_NEGLIGIBLE_BELOW_C

    assert ICING_TEMPERATURE_LOWER_C == -40.0
    assert ICING_POTENTIAL_NEGLIGIBLE_BELOW_C == -35.0
    assert ICING_TEMPERATURE_LOWER_C != ICING_POTENTIAL_NEGLIGIBLE_BELOW_C


def test_taf_change_indicator_meaning_covers_every_real_change_type_the_decoder_produces():
    """Decode a real, multi-group TAF and check every real
    change_type value TAFDecoder actually produces has a defined
    meaning - not a fixed, possibly-stale list."""
    from awci.knowledge.icao.taf_change_indicators import TAF_CHANGE_INDICATOR_MEANING
    from awci.knowledge.icao.taf_decoder import TAFDecoder

    raw = (
        "TAF LFPG 021100Z 0212/0318 24010KT 9999 SCT030 "
        "BECMG 0215/0217 25015KT "
        "TEMPO 0218/0221 4000 TSRA "
        "PROB30 TEMPO 0300/0304 0800 FG"
    )
    report = TAFDecoder.decode(raw)
    assert len(report.periods) > 1
    for period in report.periods:
        assert period.change_type in TAF_CHANGE_INDICATOR_MEANING, period.change_type
        assert TAF_CHANGE_INDICATOR_MEANING[period.change_type]


def test_taf_no_significant_weather_code_is_real_and_distinct_from_an_omitted_group():
    from awci.knowledge.icao.taf_change_indicators import TAF_NO_SIGNIFICANT_WEATHER_CODE

    assert TAF_NO_SIGNIFICANT_WEATHER_CODE == "NSW"


def test_sigmet_validity_hours_match_the_real_icao_annex_3_rules():
    from awci.knowledge.icao.sigmet_validity import (
        SIGMET_MAX_LEAD_TIME_HOURS_WC_WV,
        SIGMET_MAX_LEAD_TIME_HOURS_WS,
        SIGMET_MAX_VALIDITY_HOURS_WC_WV,
        SIGMET_MAX_VALIDITY_HOURS_WS,
    )

    assert SIGMET_MAX_VALIDITY_HOURS_WS == 4.0
    assert SIGMET_MAX_VALIDITY_HOURS_WC_WV == 6.0
    assert SIGMET_MAX_LEAD_TIME_HOURS_WS == 4.0
    assert SIGMET_MAX_LEAD_TIME_HOURS_WC_WV == 12.0
    # Real, disclosed relationship: the longer-lived phenomena (tropical
    # cyclone/volcanic ash) get both a longer validity and a longer
    # permitted lead time than ordinary hazardous weather.
    assert SIGMET_MAX_VALIDITY_HOURS_WC_WV > SIGMET_MAX_VALIDITY_HOURS_WS
    assert SIGMET_MAX_LEAD_TIME_HOURS_WC_WV > SIGMET_MAX_LEAD_TIME_HOURS_WS


def test_sigmet_phenomenon_keywords_already_cover_every_real_phenomenon_from_the_source():
    """No new SIGMET phenomenon keywords were needed - the real decoder
    already covers every phenomenon this source describes (SEV TURB,
    SEV ICE, SEV MTW, thunderstorm variants, HVY DS/SS, VA, TC,
    RDOACT CLD) - locks in that finding rather than leaving it only in
    a commit message."""
    from awci.knowledge.icao.sigmet_decoder import _PHENOMENON_KEYWORDS

    for keyword in ("SEV TURB", "SEV ICE", "SEV MTW", "HVY DS", "HVY SS", "VA", "TC", "RDOACT CLD"):
        assert keyword in _PHENOMENON_KEYWORDS


def test_airmet_wind_gust_threshold_matches_the_real_icao_value():
    from awci.knowledge.icao.gamet_airmet import AIRMET_PHENOMENA, AIRMET_SURFACE_WIND_GUST_THRESHOLD_KT

    assert AIRMET_SURFACE_WIND_GUST_THRESHOLD_KT == 40.0
    assert len(AIRMET_PHENOMENA) == 7
    assert "freezing rain" in AIRMET_PHENOMENA


def test_runway_contamination_minimum_depth_matches_the_real_easa_thresholds():
    from awci.knowledge.airports.runway_state import RUNWAY_CONTAMINATION_MINIMUM_DEPTH_MM

    assert RUNWAY_CONTAMINATION_MINIMUM_DEPTH_MM["dry_or_wet_snow"] == 3.0
    assert RUNWAY_CONTAMINATION_MINIMUM_DEPTH_MM["water_or_slush"] == 3.0
    assert RUNWAY_CONTAMINATION_MINIMUM_DEPTH_MM["compacted_snow"] is None
    assert RUNWAY_CONTAMINATION_MINIMUM_DEPTH_MM["ice"] is None


def test_hydroplaning_coefficient_discrepancy_is_disclosed_not_silently_merged():
    """acf.science.encyclopedia.aviation_extended already implements
    and cites the real Vp = 9*sqrt(p_psi) dynamic hydroplaning speed
    formula (Horonjeff & McKelvey); this module's own alternate
    source cites 8.73 - a real, disclosed discrepancy between two
    real, independently cited references, deliberately not merged
    into the existing, already-working formula."""
    from acf.science.encyclopedia.aviation_extended import calculate_hydroplaning_speed_knots
    from awci.knowledge.airports.runway_state import DYNAMIC_HYDROPLANING_SPEED_COEFFICIENT_ALTERNATE_SOURCE

    tire_pressure_psi = 121.0
    existing_speed_kt = calculate_hydroplaning_speed_knots(tire_pressure_psi)
    alternate_speed_kt = DYNAMIC_HYDROPLANING_SPEED_COEFFICIENT_ALTERNATE_SOURCE * tire_pressure_psi**0.5

    assert existing_speed_kt == pytest.approx(99.0)
    assert alternate_speed_kt == pytest.approx(96.03, abs=0.01)
    assert existing_speed_kt != pytest.approx(alternate_speed_kt, abs=0.5)


def test_thunderstorm_stages_cover_the_real_three_stage_life_cycle():
    from awci.knowledge.meteorology.thunderstorm import ThunderstormStage

    assert {stage.value for stage in ThunderstormStage} == {"cumulus", "mature", "dissipating"}


def test_thunderstorm_mature_stage_updraft_exceeds_downdraft():
    from awci.knowledge.meteorology.thunderstorm import (
        THUNDERSTORM_MATURE_DOWNDRAFT_M_S,
        THUNDERSTORM_MATURE_UPDRAFT_M_S,
    )

    assert THUNDERSTORM_MATURE_UPDRAFT_M_S == 35.0
    assert THUNDERSTORM_MATURE_DOWNDRAFT_M_S == 15.0
    assert THUNDERSTORM_MATURE_UPDRAFT_M_S > THUNDERSTORM_MATURE_DOWNDRAFT_M_S


def test_hail_fall_velocity_increases_monotonically_with_diameter():
    from awci.knowledge.meteorology.thunderstorm import HAIL_DIAMETER_MM_TO_FALL_VELOCITY_KMH

    diameters = sorted(HAIL_DIAMETER_MM_TO_FALL_VELOCITY_KMH)
    velocities = [HAIL_DIAMETER_MM_TO_FALL_VELOCITY_KMH[d] for d in diameters]
    assert velocities == sorted(velocities)


def test_thunderstorm_reference_values_are_all_real_and_positive():
    from awci.knowledge.meteorology.thunderstorm import (
        AIRLINER_LIGHTNING_STRIKES_PER_YEAR_APPROX,
        CUMULONIMBUS_ANVIL_ALTITUDE_M,
        HAIL_DIAMETER_MAXIMUM_DOCUMENTED_MM,
        LIGHTNING_PEAK_CURRENT_AMPERES_APPROX,
        THUNDERSTORM_DISSIPATION_TIME_MINUTES,
        THUNDERSTORM_TURBULENCE_LATERAL_EXTENT_NM,
    )

    assert THUNDERSTORM_DISSIPATION_TIME_MINUTES == 30.0
    assert CUMULONIMBUS_ANVIL_ALTITUDE_M == 15_000.0
    assert THUNDERSTORM_TURBULENCE_LATERAL_EXTENT_NM == (10.0, 20.0)
    assert AIRLINER_LIGHTNING_STRIKES_PER_YEAR_APPROX == 1.0
    assert LIGHTNING_PEAK_CURRENT_AMPERES_APPROX == 200_000.0
    assert HAIL_DIAMETER_MAXIMUM_DOCUMENTED_MM == 150.0


def test_orographic_wave_wind_and_slope_thresholds_are_real_and_positive():
    from awci.knowledge.meteorology.orographic_turbulence import (
        OROGRAPHIC_WAVE_MINIMUM_WIND_SPEED_KT,
        OROGRAPHIC_WAVE_ROTOR_CRITICAL_SLOPE_DEG,
    )

    assert OROGRAPHIC_WAVE_MINIMUM_WIND_SPEED_KT == 25.0
    assert OROGRAPHIC_WAVE_ROTOR_CRITICAL_SLOPE_DEG == 40.0


def test_orographic_wave_rotor_descent_speed_range_is_ordered():
    from awci.knowledge.meteorology.orographic_turbulence import (
        OROGRAPHIC_WAVE_ROTOR_DESCENT_SPEED_KMH,
    )

    low, high = OROGRAPHIC_WAVE_ROTOR_DESCENT_SPEED_KMH
    assert low == 20.0
    assert high == 36.0
    assert low < high


def test_orographic_wave_downwind_extent_is_real_and_positive():
    from awci.knowledge.meteorology.orographic_turbulence import (
        OROGRAPHIC_WAVE_MINIMUM_DOWNWIND_EXTENT_KM,
    )

    assert OROGRAPHIC_WAVE_MINIMUM_DOWNWIND_EXTENT_KM == 100.0


def test_orographic_wave_stability_outcomes_are_qualitatively_distinct():
    from awci.knowledge.meteorology.orographic_turbulence import (
        OROGRAPHIC_WAVE_STABLE_AIR_OUTCOME,
        OROGRAPHIC_WAVE_UNSTABLE_AIR_OUTCOME,
    )

    assert OROGRAPHIC_WAVE_STABLE_AIR_OUTCOME != OROGRAPHIC_WAVE_UNSTABLE_AIR_OUTCOME
    assert "descent" in OROGRAPHIC_WAVE_STABLE_AIR_OUTCOME
    assert "lifting" in OROGRAPHIC_WAVE_UNSTABLE_AIR_OUTCOME


def test_orographic_turbulence_reference_is_complementary_to_the_froude_diagnostic():
    """The real formation-condition facts here (wind/slope thresholds,
    rotor speed) are independent of and do not duplicate the real
    per-point Fr = U/(N*H) diagnostic already implemented in
    awci.hazards.orographic_froude - both modules can coexist without
    overlap."""
    import awci.hazards.orographic_froude as froude_module
    import awci.knowledge.meteorology.orographic_turbulence as reference_module

    froude_names = set(dir(froude_module))
    reference_names = {
        name for name in dir(reference_module) if name.isupper()
    }
    assert froude_names.isdisjoint(reference_names)


def test_cat_typical_altitude_range_is_real_and_matches_metres_to_feet():
    from awci.knowledge.meteorology.clear_air_turbulence import (
        CAT_TYPICAL_ALTITUDE_RANGE_FT,
        CAT_TYPICAL_ALTITUDE_RANGE_M,
    )

    assert CAT_TYPICAL_ALTITUDE_RANGE_M == (7_000.0, 12_000.0)
    assert CAT_TYPICAL_ALTITUDE_RANGE_FT == (23_000.0, 39_000.0)
    low_m, high_m = CAT_TYPICAL_ALTITUDE_RANGE_M
    low_ft, high_ft = CAT_TYPICAL_ALTITUDE_RANGE_FT
    # Real unit-conversion sanity check (1 m ~= 3.281 ft), not a fabricated relation.
    assert low_ft == pytest.approx(low_m * 3.28084, rel=0.02)
    assert high_ft == pytest.approx(high_m * 3.28084, rel=0.02)


def test_cat_is_associated_with_jet_stream_regions():
    from awci.knowledge.meteorology.clear_air_turbulence import CAT_ASSOCIATED_WITH_JET_STREAM

    assert CAT_ASSOCIATED_WITH_JET_STREAM is True


def test_cat_example_jet_stream_data_point_is_real_and_within_the_turbulence_band():
    from awci.knowledge.meteorology.clear_air_turbulence import (
        CAT_EXAMPLE_JET_STREAM_CORE_FLIGHT_LEVEL,
        CAT_EXAMPLE_JET_STREAM_CORE_SPEED_KT,
        CAT_EXAMPLE_TURBULENCE_FLIGHT_LEVEL_RANGE,
    )

    assert CAT_EXAMPLE_JET_STREAM_CORE_SPEED_KT == 130.0
    assert CAT_EXAMPLE_JET_STREAM_CORE_FLIGHT_LEVEL == 340
    low_fl, high_fl = CAT_EXAMPLE_TURBULENCE_FLIGHT_LEVEL_RANGE
    assert low_fl < CAT_EXAMPLE_JET_STREAM_CORE_FLIGHT_LEVEL < high_fl


def test_cat_is_more_severe_on_the_cold_air_side():
    from awci.knowledge.meteorology.clear_air_turbulence import CAT_MORE_SEVERE_ON_COLD_AIR_SIDE

    assert CAT_MORE_SEVERE_ON_COLD_AIR_SIDE is True


def test_cat_reference_is_complementary_to_the_ellrod_knapp_index():
    """The real altitude-band/jet-stream/asymmetry facts here are
    independent of and do not duplicate the real per-point Ellrod &
    Knapp (1992) TI2/EI diagnostic already implemented in
    awci.hazards.cat_turbulence - both modules can coexist without
    overlap."""
    import awci.hazards.cat_turbulence as index_module
    import awci.knowledge.meteorology.clear_air_turbulence as reference_module

    index_names = set(dir(index_module))
    reference_names = {
        name for name in dir(reference_module) if name.isupper()
    }
    assert index_names.isdisjoint(reference_names)


def test_fog_types_cover_the_five_real_formation_mechanisms():
    from awci.knowledge.meteorology.fog import FogType

    assert {fog_type.value for fog_type in FogType} == {
        "radiation",
        "advection",
        "evaporation",
        "slope",
        "freezing",
    }


def test_mist_and_fog_visibility_definitions_are_ordered_and_real():
    from awci.knowledge.meteorology.fog import (
        FOG_VISIBILITY_MAX_KM,
        MIST_VISIBILITY_RANGE_KM,
    )

    assert FOG_VISIBILITY_MAX_KM == 1.0
    low, high = MIST_VISIBILITY_RANGE_KM
    assert low == 1.0
    assert high == 5.0
    assert FOG_VISIBILITY_MAX_KM <= low


def test_fog_droplet_size_is_smaller_than_mist_droplet_diameter_upper_bound():
    from awci.knowledge.meteorology.fog import (
        FOG_DROPLET_DIAMETER_RANGE_MICRONS,
        MIST_DROPLET_DIAMETER_MICRONS_APPROX,
    )

    low, high = FOG_DROPLET_DIAMETER_RANGE_MICRONS
    assert low == 1.0
    assert high == 10.0
    assert MIST_DROPLET_DIAMETER_MICRONS_APPROX == 1.0
    assert MIST_DROPLET_DIAMETER_MICRONS_APPROX <= low


def test_radiation_fog_wind_speed_window_is_light_and_ordered():
    from awci.knowledge.meteorology.fog import RADIATION_FOG_WIND_SPEED_RANGE_KT

    low, high = RADIATION_FOG_WIND_SPEED_RANGE_KT
    assert low == 1.0
    assert high == 3.0
    assert low < high


def test_advection_fog_formation_conditions_are_real_and_positive():
    from awci.knowledge.meteorology.fog import (
        ADVECTION_FOG_TEMPERATURE_DIFFERENCE_MAX_C,
        ADVECTION_FOG_WIND_SPEED_MIN_MS,
        ADVECTION_FOG_WIND_SPEED_OFFSHORE_RANGE_MS,
    )

    assert ADVECTION_FOG_TEMPERATURE_DIFFERENCE_MAX_C == 10.0
    assert ADVECTION_FOG_WIND_SPEED_MIN_MS == 2.0
    offshore_low, offshore_high = ADVECTION_FOG_WIND_SPEED_OFFSHORE_RANGE_MS
    assert offshore_low == 20.0
    assert offshore_high == 30.0
    assert ADVECTION_FOG_WIND_SPEED_MIN_MS < offshore_low


def test_evaporation_fog_spatial_limits_are_real_and_positive():
    from awci.knowledge.meteorology.fog import (
        EVAPORATION_FOG_MAXIMUM_DISTANCE_FROM_COAST_NM,
        EVAPORATION_FOG_MAXIMUM_THICKNESS_M,
    )

    assert EVAPORATION_FOG_MAXIMUM_DISTANCE_FROM_COAST_NM == 5.0
    assert EVAPORATION_FOG_MAXIMUM_THICKNESS_M == 50.0


def test_fog_reference_is_complementary_to_the_visibility_risk_proxy():
    """The real classification facts here (droplet size, formation
    wind-speed windows, coastal/thickness limits) are independent of
    and do not duplicate the real per-point visibility_risk_score
    already computed in awci.hazards.visibility - both modules can
    coexist without overlap."""
    import awci.hazards.visibility as risk_module
    import awci.knowledge.meteorology.fog as reference_module

    risk_names = set(dir(risk_module))
    reference_names = {
        name for name in dir(reference_module) if name.isupper()
    }
    assert risk_names.isdisjoint(reference_names)


def test_wind_gradient_exceptional_magnitude_and_rate_are_real_and_positive():
    from awci.knowledge.meteorology.low_level_wind_gradient import (
        WIND_GRADIENT_EXCEPTIONAL_AMPLITUDE_KT,
        WIND_GRADIENT_EXCEPTIONAL_RATE_KT_PER_S,
    )

    assert WIND_GRADIENT_EXCEPTIONAL_AMPLITUDE_KT == 70.0
    assert WIND_GRADIENT_EXCEPTIONAL_RATE_KT_PER_S == 25.0


def test_wind_gradient_critical_altitude_and_recovery_rate_are_real():
    from awci.knowledge.meteorology.low_level_wind_gradient import (
        AIRCRAFT_GO_AROUND_ACCELERATION_KT_PER_S,
        WIND_GRADIENT_CRITICAL_ALTITUDE_FT,
    )

    assert WIND_GRADIENT_CRITICAL_ALTITUDE_FT == 500.0
    assert AIRCRAFT_GO_AROUND_ACCELERATION_KT_PER_S == 2.0


def test_wind_gradient_reference_is_complementary_to_the_bulk_shear_diagnostic():
    """The real approach-phase operational facts here are independent
    of and do not duplicate the real per-point bulk wind shear already
    computed in awci.hazards.wind_shear - both modules can coexist
    without overlap."""
    import awci.hazards.wind_shear as shear_module
    import awci.knowledge.meteorology.low_level_wind_gradient as reference_module

    shear_names = set(dir(shear_module))
    reference_names = {
        name for name in dir(reference_module) if name.isupper()
    }
    assert shear_names.isdisjoint(reference_names)


def test_microburst_peak_wind_speed_units_are_mutually_consistent():
    from awci.knowledge.meteorology.microburst_reference import (
        MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_KMH,
        MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_MS,
    )

    assert MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_MS == 75.0
    assert MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_KMH == 270.0
    # Real unit-conversion sanity check (1 m/s = 3.6 km/h), not a fabricated relation.
    assert MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_KMH == pytest.approx(
        MICROBURST_PEAK_HORIZONTAL_WIND_SPEED_MS * 3.6, rel=0.01
    )


def test_microburst_vertical_speed_and_duration_and_diameter_ranges_are_ordered():
    from awci.knowledge.meteorology.microburst_reference import (
        MICROBURST_PEAK_VERTICAL_SPEED_RANGE_FT_MIN,
        MICROBURST_TYPICAL_DIAMETER_RANGE_KM,
        MICROBURST_TYPICAL_DURATION_RANGE_MINUTES,
    )

    v_low, v_high = MICROBURST_PEAK_VERTICAL_SPEED_RANGE_FT_MIN
    assert v_low == 720.0
    assert v_high == 1200.0
    assert v_low < v_high

    d_low, d_high = MICROBURST_TYPICAL_DURATION_RANGE_MINUTES
    assert d_low == 5.0
    assert d_high == 15.0
    assert d_low < d_high

    km_low, km_high = MICROBURST_TYPICAL_DIAMETER_RANGE_KM
    assert km_low == 1.0
    assert km_high == 4.0
    assert km_low < km_high


def test_microburst_significant_shear_altitude_band_and_magnitude_are_real():
    from awci.knowledge.meteorology.microburst_reference import (
        MICROBURST_SIGNIFICANT_SHEAR_ALTITUDE_BAND_FT,
        MICROBURST_SIGNIFICANT_SHEAR_MAGNITUDE_KT,
    )

    assert MICROBURST_SIGNIFICANT_SHEAR_ALTITUDE_BAND_FT == 3_000.0
    assert MICROBURST_SIGNIFICANT_SHEAR_MAGNITUDE_KT == 60.0


def test_llwas_and_pws_detection_system_parameters_are_real_and_positive():
    from awci.knowledge.meteorology.microburst_reference import (
        LLWAS_MAXIMUM_ANEMOMETER_COUNT,
        LLWAS_MAXIMUM_TRAJECTORY_DISTANCE_NM,
        PWS_ACTIVE_ALTITUDE_MAX_FT_AGL,
        PWS_DETECTION_RANGE_NM,
        PWS_MINIMUM_WARNING_TIME_S,
        PWS_TYPICAL_WARNING_TIME_S,
    )

    assert LLWAS_MAXIMUM_ANEMOMETER_COUNT == 30
    assert LLWAS_MAXIMUM_TRAJECTORY_DISTANCE_NM == 3.0
    assert PWS_MINIMUM_WARNING_TIME_S == 10.0
    assert PWS_TYPICAL_WARNING_TIME_S == 60.0
    assert PWS_MINIMUM_WARNING_TIME_S < PWS_TYPICAL_WARNING_TIME_S
    range_low, range_high = PWS_DETECTION_RANGE_NM
    assert range_low == 0.5
    assert range_high == 5.0
    assert PWS_ACTIVE_ALTITUDE_MAX_FT_AGL == 1_500.0


def test_microburst_reference_is_complementary_to_the_alert_proximity_diagnostic():
    """The real physical-scale/detection-system facts here are
    independent of and do not duplicate the real, cited ICAO 30 kt /
    1500 ft alert-proximity threshold already computed in
    awci.hazards.microburst - both modules can coexist without
    overlap."""
    import awci.hazards.microburst as alert_module
    import awci.knowledge.meteorology.microburst_reference as reference_module

    alert_names = set(dir(alert_module))
    reference_names = {
        name for name in dir(reference_module) if name.isupper()
    }
    assert alert_names.isdisjoint(reference_names)


def test_squall_line_types_cover_the_real_dry_and_wet_distinction():
    from awci.knowledge.meteorology.squall_line import SquallLineType

    assert {squall_type.value for squall_type in SquallLineType} == {"white", "black"}


def test_squall_gust_excess_threshold_and_measurement_period_are_real():
    from awci.knowledge.meteorology.squall_line import (
        SQUALL_GUST_EXCESS_MEASUREMENT_PERIOD_MINUTES,
        SQUALL_MINIMUM_GUST_EXCESS_KT,
    )

    assert SQUALL_MINIMUM_GUST_EXCESS_KT == 15.0
    assert SQUALL_GUST_EXCESS_MEASUREMENT_PERIOD_MINUTES == 1.0


def test_squall_wind_direction_shift_range_is_ordered_and_real():
    from awci.knowledge.meteorology.squall_line import SQUALL_WIND_DIRECTION_SHIFT_RANGE_DEG

    low, high = SQUALL_WIND_DIRECTION_SHIFT_RANGE_DEG
    assert low == 45.0
    assert high == 90.0
    assert low < high


def test_squall_macro_micro_corridor_width_threshold_is_distinct_from_microburst_diameter():
    """The real macro-/micro-rafale corridor-width cutoff (a squall-
    gust naming convention) is a different real quantity from the real
    individual-microburst physical diameter range already recorded in
    awci.knowledge.meteorology.microburst_reference - not the same
    fact, not duplicated."""
    from awci.knowledge.meteorology.microburst_reference import MICROBURST_TYPICAL_DIAMETER_RANGE_KM
    from awci.knowledge.meteorology.squall_line import SQUALL_MACRO_MICRO_CORRIDOR_WIDTH_THRESHOLD_KM

    assert SQUALL_MACRO_MICRO_CORRIDOR_WIDTH_THRESHOLD_KM == 2.5
    assert SQUALL_MACRO_MICRO_CORRIDOR_WIDTH_THRESHOLD_KM != MICROBURST_TYPICAL_DIAMETER_RANGE_KM[0]


def test_turbulence_intensity_covers_the_real_four_level_pirep_style_scale():
    from awci.knowledge.meteorology.turbulence_intensity import TurbulenceIntensity

    assert {intensity.value for intensity in TurbulenceIntensity} == {
        "light",
        "moderate",
        "severe",
        "extreme",
    }


def test_every_turbulence_intensity_has_a_real_qualitative_description():
    from awci.knowledge.meteorology.turbulence_intensity import (
        TURBULENCE_INTENSITY_DESCRIPTION,
        TurbulenceIntensity,
    )

    for intensity in TurbulenceIntensity:
        assert intensity in TURBULENCE_INTENSITY_DESCRIPTION
        assert len(TURBULENCE_INTENSITY_DESCRIPTION[intensity]) > 0


def test_turbulence_source_covers_the_real_nine_origin_categories():
    from awci.knowledge.meteorology.turbulence_intensity import TurbulenceSource

    assert {source.value for source in TurbulenceSource} == {
        "friction",
        "obstacle",
        "orographic",
        "clear_air",
        "frontal",
        "sea_breeze",
        "aircraft_wake",
        "cloud_wake",
        "thermal_convective",
    }


def test_turbulence_intensity_reference_is_complementary_to_the_ellrod_knapp_category_labels():
    """The real qualitative PIREP-style intensity scale here is
    independent of and does not duplicate the real, numerically-derived
    Ellrod & Knapp (1992) TI2/EI severity labels already returned by
    acf.science.turbulence.wind_turbulence.CATIndex.category() - both
    can coexist without overlap."""
    from acf.science.turbulence.wind_turbulence import CATIndex
    import awci.knowledge.meteorology.turbulence_intensity as reference_module

    cat_index_names = set(dir(CATIndex))
    reference_names = {
        name for name in dir(reference_module) if name.isupper()
    }
    assert cat_index_names.isdisjoint(reference_names)


def test_jet_stream_types_cover_the_three_real_named_types():
    from awci.knowledge.meteorology.jet_stream import JetStreamType

    assert {jet_type.value for jet_type in JetStreamType} == {
        "polar",
        "subtropical",
        "equatorial_easterly",
    }


def test_polar_jet_peak_speed_and_latitude_band_are_real():
    from awci.knowledge.meteorology.jet_stream import (
        POLAR_JET_LATITUDE_RANGE_DEG,
        POLAR_JET_PEAK_WIND_SPEED_KT,
    )

    assert POLAR_JET_PEAK_WIND_SPEED_KT == 160.0
    low, high = POLAR_JET_LATITUDE_RANGE_DEG
    assert low == 35.0
    assert high == 70.0
    assert low < high


def test_subtropical_jet_speed_altitude_and_latitude_are_real_and_ordered():
    from awci.knowledge.meteorology.jet_stream import (
        SUBTROPICAL_JET_CORE_ALTITUDE_RANGE_FT,
        SUBTROPICAL_JET_LATITUDE_RANGE_DEG,
        SUBTROPICAL_JET_PEAK_WIND_SPEED_KT,
        SUBTROPICAL_JET_WIND_SPEED_RANGE_KT,
    )

    speed_low, speed_high = SUBTROPICAL_JET_WIND_SPEED_RANGE_KT
    assert speed_low == 120.0
    assert speed_high == 150.0
    assert speed_high < SUBTROPICAL_JET_PEAK_WIND_SPEED_KT
    assert SUBTROPICAL_JET_PEAK_WIND_SPEED_KT == 250.0

    alt_low, alt_high = SUBTROPICAL_JET_CORE_ALTITUDE_RANGE_FT
    assert alt_low == 35_000.0
    assert alt_high == 40_000.0

    lat_low, lat_high = SUBTROPICAL_JET_LATITUDE_RANGE_DEG
    assert lat_low == 20.0
    assert lat_high == 40.0


def test_equatorial_easterly_jet_speed_and_altitude_are_real():
    from awci.knowledge.meteorology.jet_stream import (
        EQUATORIAL_EASTERLY_JET_ALTITUDE_KM_APPROX,
        EQUATORIAL_EASTERLY_JET_WIND_SPEED_RANGE_KT,
    )

    low, high = EQUATORIAL_EASTERLY_JET_WIND_SPEED_RANGE_KT
    assert low == 80.0
    assert high == 90.0
    assert EQUATORIAL_EASTERLY_JET_ALTITUDE_KM_APPROX == 15.0


def test_jet_stream_shear_gradients_are_real_and_ordered():
    from awci.knowledge.meteorology.jet_stream import (
        JET_STREAM_ANTICYCLONIC_SIDE_SHEAR_KT_PER_100NM,
        JET_STREAM_CYCLONIC_SIDE_SHEAR_KT_PER_100NM,
        JET_STREAM_HORIZONTAL_SHEAR_KT_PER_100NM_RANGE,
        JET_STREAM_VERTICAL_SHEAR_KT_PER_1000FT_RANGE,
    )

    v_low, v_high = JET_STREAM_VERTICAL_SHEAR_KT_PER_1000FT_RANGE
    assert v_low == 5.0
    assert v_high == 10.0
    h_low, h_high = JET_STREAM_HORIZONTAL_SHEAR_KT_PER_100NM_RANGE
    assert h_low == 20.0
    assert h_high == 30.0
    assert JET_STREAM_CYCLONIC_SIDE_SHEAR_KT_PER_100NM == 45.0
    assert JET_STREAM_ANTICYCLONIC_SIDE_SHEAR_KT_PER_100NM == 20.0
    assert JET_STREAM_CYCLONIC_SIDE_SHEAR_KT_PER_100NM > JET_STREAM_ANTICYCLONIC_SIDE_SHEAR_KT_PER_100NM


def test_jet_stream_dimension_descriptions_are_present_and_non_fabricated():
    """These are real, order-of-magnitude descriptions - the source
    gives no precise numeric range, so none is fabricated here."""
    from awci.knowledge.meteorology.jet_stream import (
        JET_STREAM_TYPICAL_LENGTH_DESCRIPTION,
        JET_STREAM_TYPICAL_THICKNESS_DESCRIPTION,
        JET_STREAM_TYPICAL_WIDTH_DESCRIPTION,
    )

    assert "thousand" in JET_STREAM_TYPICAL_LENGTH_DESCRIPTION
    assert "hundred" in JET_STREAM_TYPICAL_WIDTH_DESCRIPTION
    assert "few kilometres" in JET_STREAM_TYPICAL_THICKNESS_DESCRIPTION


def test_jet_stream_reference_is_complementary_to_the_cat_example_data_point():
    """The real general per-type facts here are independent of and do
    not duplicate the real single-example jet-stream data point already
    recorded in awci.knowledge.meteorology.clear_air_turbulence (a
    specific 130 kt/FL340 TEMSI chart observation) - both can coexist
    without overlap."""
    import awci.knowledge.meteorology.clear_air_turbulence as cat_module
    import awci.knowledge.meteorology.jet_stream as jet_module

    cat_names = {name for name in dir(cat_module) if name.isupper()}
    jet_names = {name for name in dir(jet_module) if name.isupper()}
    assert cat_names.isdisjoint(jet_names)


def test_front_types_cover_the_four_real_classical_types():
    from awci.knowledge.meteorology.weather_front import FrontType

    assert {front_type.value for front_type in FrontType} == {
        "warm",
        "cold",
        "occluded",
        "stationary",
    }


def test_cold_front_is_faster_than_warm_front():
    from awci.knowledge.meteorology.weather_front import COLD_FRONT_FASTER_THAN_WARM_FRONT

    assert COLD_FRONT_FASTER_THAN_WARM_FRONT is True


def test_warm_and_cold_front_cloud_sequences_use_real_wmo_cloud_genera():
    from awci.knowledge.meteorology.clouds import CloudGenus
    from awci.knowledge.meteorology.weather_front import (
        COLD_FRONT_CLOUD_SEQUENCE,
        WARM_FRONT_CLOUD_SEQUENCE,
    )

    assert len(WARM_FRONT_CLOUD_SEQUENCE) == 7
    assert len(COLD_FRONT_CLOUD_SEQUENCE) == 6
    for genus in WARM_FRONT_CLOUD_SEQUENCE + COLD_FRONT_CLOUD_SEQUENCE:
        assert isinstance(genus, CloudGenus)
    assert WARM_FRONT_CLOUD_SEQUENCE[0] == CloudGenus.CIRRUS
    assert WARM_FRONT_CLOUD_SEQUENCE[-1] == CloudGenus.STRATUS
    assert COLD_FRONT_CLOUD_SEQUENCE[0] == CloudGenus.CIRRUS
    assert WARM_FRONT_CLOUD_SEQUENCE != COLD_FRONT_CLOUD_SEQUENCE


def test_front_structural_and_persistence_descriptions_are_present():
    from awci.knowledge.meteorology.weather_front import (
        KATABATIC_COLD_FRONT_FEATURE_DESCRIPTION,
        OCCLUDED_FRONT_FORMATION_DESCRIPTION,
        STATIONARY_FRONT_PERSISTENCE_DESCRIPTION,
    )

    assert "several days" in STATIONARY_FRONT_PERSISTENCE_DESCRIPTION
    assert "cold front" in OCCLUDED_FRONT_FORMATION_DESCRIPTION
    assert "warm front" in OCCLUDED_FRONT_FORMATION_DESCRIPTION
    assert "dry-air" in KATABATIC_COLD_FRONT_FEATURE_DESCRIPTION


def test_circulation_cell_latitude_bands_are_real_and_contiguous():
    from awci.knowledge.meteorology.general_circulation import (
        FERREL_CELL_LATITUDE_RANGE_DEG,
        HADLEY_CELL_LATITUDE_RANGE_DEG,
        POLAR_CELL_LATITUDE_RANGE_DEG,
    )

    assert HADLEY_CELL_LATITUDE_RANGE_DEG == (0.0, 30.0)
    assert FERREL_CELL_LATITUDE_RANGE_DEG == (30.0, 60.0)
    assert POLAR_CELL_LATITUDE_RANGE_DEG == (60.0, 90.0)
    assert HADLEY_CELL_LATITUDE_RANGE_DEG[1] == FERREL_CELL_LATITUDE_RANGE_DEG[0]
    assert FERREL_CELL_LATITUDE_RANGE_DEG[1] == POLAR_CELL_LATITUDE_RANGE_DEG[0]


def test_ferrel_polar_convergence_latitude_is_real_and_ordered():
    from awci.knowledge.meteorology.general_circulation import (
        FERREL_CELL_LATITUDE_RANGE_DEG,
        FERREL_POLAR_CONVERGENCE_LATITUDE_RANGE_DEG,
    )

    low, high = FERREL_POLAR_CONVERGENCE_LATITUDE_RANGE_DEG
    assert low == 60.0
    assert high == 70.0
    assert low >= FERREL_CELL_LATITUDE_RANGE_DEG[1]


def test_general_circulation_jet_stream_altitude_is_distinct_from_per_type_jet_facts():
    """The real, general circulation-cell-context jet-stream altitude
    band here is independent of and does not duplicate the real
    per-type jet-core altitude/speed facts already recorded in
    awci.knowledge.meteorology.jet_stream - both can coexist without
    overlap."""
    import awci.knowledge.meteorology.general_circulation as circulation_module
    import awci.knowledge.meteorology.jet_stream as jet_module

    circulation_names = {name for name in dir(circulation_module) if name.isupper()}
    jet_names = {name for name in dir(jet_module) if name.isupper()}
    assert circulation_names.isdisjoint(jet_names)

    from awci.knowledge.meteorology.general_circulation import (
        GENERAL_CIRCULATION_JET_STREAM_ALTITUDE_RANGE_KM,
    )

    low, high = GENERAL_CIRCULATION_JET_STREAM_ALTITUDE_RANGE_KM
    assert low == 6.0
    assert high == 15.0


def test_trade_wind_extent_and_speed_are_real_and_positive():
    from awci.knowledge.meteorology.general_circulation import (
        TRADE_WIND_TYPICAL_SPEED_KMH_APPROX,
        TRADE_WIND_VERTICAL_EXTENT_RANGE_M,
    )

    low, high = TRADE_WIND_VERTICAL_EXTENT_RANGE_M
    assert low == 1_500.0
    assert high == 2_000.0
    assert TRADE_WIND_TYPICAL_SPEED_KMH_APPROX == 20.0


def test_itcz_seasonal_lag_and_latitude_facts_are_real_and_ordered():
    from awci.knowledge.meteorology.general_circulation import (
        ITCZ_EAST_ASIA_SUMMER_MAXIMUM_LATITUDE_DEG_N,
        ITCZ_JULY_AUGUST_OCEANIC_LATITUDE_RANGE_DEG_N,
        ITCZ_SEASONAL_LAG_RANGE_MONTHS,
    )

    lag_low, lag_high = ITCZ_SEASONAL_LAG_RANGE_MONTHS
    assert lag_low == 1.0
    assert lag_high == 2.0

    lat_low, lat_high = ITCZ_JULY_AUGUST_OCEANIC_LATITUDE_RANGE_DEG_N
    assert lat_low == 5.0
    assert lat_high == 15.0
    assert ITCZ_EAST_ASIA_SUMMER_MAXIMUM_LATITUDE_DEG_N == 30.0
    assert ITCZ_EAST_ASIA_SUMMER_MAXIMUM_LATITUDE_DEG_N > lat_high


def test_itcz_cumulonimbus_maximum_top_altitude_is_real():
    from awci.knowledge.meteorology.general_circulation import (
        ITCZ_CUMULONIMBUS_MAXIMUM_TOP_ALTITUDE_FT_APPROX,
    )

    assert ITCZ_CUMULONIMBUS_MAXIMUM_TOP_ALTITUDE_FT_APPROX == 55_000.0


def test_dry_air_composition_percentages_sum_close_to_100():
    from awci.knowledge.meteorology.atmosphere_composition import (
        DRY_AIR_ARGON_PERCENT,
        DRY_AIR_CARBON_DIOXIDE_PERCENT,
        DRY_AIR_NITROGEN_PERCENT,
        DRY_AIR_OXYGEN_PERCENT,
        DRY_AIR_TRACE_GASES_MAXIMUM_PERCENT,
    )

    assert DRY_AIR_NITROGEN_PERCENT == 78.09
    assert DRY_AIR_OXYGEN_PERCENT == 20.95
    assert DRY_AIR_ARGON_PERCENT == 0.93
    assert DRY_AIR_CARBON_DIOXIDE_PERCENT == 0.035
    total = (
        DRY_AIR_NITROGEN_PERCENT
        + DRY_AIR_OXYGEN_PERCENT
        + DRY_AIR_ARGON_PERCENT
        + DRY_AIR_CARBON_DIOXIDE_PERCENT
        + DRY_AIR_TRACE_GASES_MAXIMUM_PERCENT
    )
    assert total == pytest.approx(100.0, abs=0.05)


def test_troposphere_observed_lapse_rate_is_disclosed_distinct_from_isa_standard():
    """A real, disclosed discrepancy - NOT merged into the existing
    ISA standard-atmosphere 6.5 degC/1000m constant already used by
    acf.science.encyclopedia.aerodynamics.isa_atmosphere - both are
    real, distinct quantities (a defined standard vs. an observed
    average) for the same physical process."""
    from awci.knowledge.meteorology.atmosphere_composition import (
        TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M,
    )

    assert TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M == 6.4
    isa_standard_lapse_rate_c_per_1000m = 6.5
    assert TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M != isa_standard_lapse_rate_c_per_1000m


def test_tropopause_altitude_is_real_and_highest_at_the_equator():
    from awci.knowledge.meteorology.atmosphere_composition import (
        TROPOPAUSE_ALTITUDE_EQUATORIAL_KM_APPROX,
        TROPOPAUSE_ALTITUDE_RANGE_POLAR_KM,
        TROPOPAUSE_ALTITUDE_RANGE_TEMPERATE_KM,
    )

    polar_low, polar_high = TROPOPAUSE_ALTITUDE_RANGE_POLAR_KM
    temperate_low, temperate_high = TROPOPAUSE_ALTITUDE_RANGE_TEMPERATE_KM
    assert polar_high == 8.0
    assert temperate_high == 12.0
    assert polar_high < temperate_high < TROPOPAUSE_ALTITUDE_EQUATORIAL_KM_APPROX
    assert TROPOPAUSE_ALTITUDE_EQUATORIAL_KM_APPROX == 18.0


def test_atmosphere_layers_are_real_and_altitude_ordered():
    from awci.knowledge.meteorology.atmosphere_composition import (
        EXOSPHERE_UPPER_LIMIT_KM_APPROX,
        MESOSPHERE_ALTITUDE_RANGE_KM,
        STRATOPAUSE_ALTITUDE_KM,
        THERMOSPHERE_ALTITUDE_RANGE_KM,
    )

    assert MESOSPHERE_ALTITUDE_RANGE_KM == (50.0, 85.0)
    assert STRATOPAUSE_ALTITUDE_KM == 50.0
    assert MESOSPHERE_ALTITUDE_RANGE_KM[0] == STRATOPAUSE_ALTITUDE_KM
    low, high = THERMOSPHERE_ALTITUDE_RANGE_KM
    assert low == 80.0
    assert high == 500.0
    assert high < EXOSPHERE_UPPER_LIMIT_KM_APPROX
    assert EXOSPHERE_UPPER_LIMIT_KM_APPROX == 10_000.0


def test_ionosphere_sublayers_are_real_and_altitude_ordered():
    from awci.knowledge.meteorology.atmosphere_composition import (
        IONOSPHERE_D_LAYER_ALTITUDE_RANGE_KM,
        IONOSPHERE_E_LAYER_ALTITUDE_RANGE_KM,
        IONOSPHERE_F_LAYER_ALTITUDE_RANGE_KM,
    )

    d_low, d_high = IONOSPHERE_D_LAYER_ALTITUDE_RANGE_KM
    e_low, e_high = IONOSPHERE_E_LAYER_ALTITUDE_RANGE_KM
    f_low, f_high = IONOSPHERE_F_LAYER_ALTITUDE_RANGE_KM
    assert d_low < e_low < f_low
    assert d_high == e_low


def test_skew_t_dry_and_moist_adiabatic_rates_are_real_and_distinct():
    """The real dry-adiabatic PARCEL rate here is a different real
    quantity from the real, observed ENVIRONMENTAL lapse rate in
    atmosphere_composition.py - both are real, standard, distinct
    meteorological quantities."""
    from awci.knowledge.meteorology.atmosphere_composition import (
        TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M,
    )
    from awci.knowledge.meteorology.skew_t_diagram import (
        DRY_ADIABATIC_LAPSE_RATE_C_PER_100M,
        MOIST_ADIABATIC_LAPSE_RATE_C_PER_1000M_TYPICAL,
        MOIST_ADIABATIC_LAPSE_RATE_RANGE_C_PER_1000M,
    )

    assert DRY_ADIABATIC_LAPSE_RATE_C_PER_100M == 1.0
    dry_rate_per_1000m = DRY_ADIABATIC_LAPSE_RATE_C_PER_100M * 10.0
    assert dry_rate_per_1000m != TROPOSPHERE_OBSERVED_AVERAGE_LAPSE_RATE_C_PER_1000M
    assert MOIST_ADIABATIC_LAPSE_RATE_C_PER_1000M_TYPICAL == 5.0
    low, high = MOIST_ADIABATIC_LAPSE_RATE_RANGE_C_PER_1000M
    assert low == 1.0
    assert high == 8.0
    assert low <= MOIST_ADIABATIC_LAPSE_RATE_C_PER_1000M_TYPICAL <= high
    assert MOIST_ADIABATIC_LAPSE_RATE_C_PER_1000M_TYPICAL < dry_rate_per_1000m


def test_radiosonde_operational_facts_are_real_and_positive():
    from awci.knowledge.meteorology.skew_t_diagram import (
        RADIOSONDE_ASCENT_DURATION_RANGE_HOURS,
        RADIOSONDE_BURST_ALTITUDE_RANGE_KM,
        RADIOSONDE_STANDARD_RELEASE_TIMES_UTC,
    )

    duration_low, duration_high = RADIOSONDE_ASCENT_DURATION_RANGE_HOURS
    assert duration_low == 2.0
    assert duration_high == 2.5
    burst_low, burst_high = RADIOSONDE_BURST_ALTITUDE_RANGE_KM
    assert burst_low == 20.0
    assert burst_high == 30.0
    assert RADIOSONDE_STANDARD_RELEASE_TIMES_UTC == ("00:00", "12:00")


def test_knot_to_kmh_conversion_is_the_real_standard_value():
    from awci.knowledge.meteorology.local_winds import KNOT_TO_KMH

    assert KNOT_TO_KMH == 1.852


def test_wind_barb_symbology_is_real_and_ordered():
    from awci.knowledge.meteorology.local_winds import (
        WIND_BARB_FULL_BARBULE_KT,
        WIND_BARB_HALF_BARBULE_KT,
        WIND_BARB_PENNANT_KT,
    )

    assert WIND_BARB_HALF_BARBULE_KT == 5.0
    assert WIND_BARB_FULL_BARBULE_KT == 10.0
    assert WIND_BARB_PENNANT_KT == 50.0
    assert WIND_BARB_HALF_BARBULE_KT < WIND_BARB_FULL_BARBULE_KT < WIND_BARB_PENNANT_KT


def test_gust_reporting_criterion_is_real():
    from awci.knowledge.meteorology.local_winds import (
        GUST_REPORTING_MINIMUM_EXCESS_KMH,
        GUST_REPORTING_MINIMUM_EXCESS_KT,
        GUST_REPORTING_MINIMUM_MEAN_WIND_KT,
    )

    assert GUST_REPORTING_MINIMUM_EXCESS_KT == 10.0
    assert GUST_REPORTING_MINIMUM_EXCESS_KMH == 19.0
    assert GUST_REPORTING_MINIMUM_MEAN_WIND_KT == 10.0


def test_local_wind_types_have_real_speed_and_extent_facts():
    from awci.knowledge.meteorology.local_winds import (
        LAND_BREEZE_TYPICAL_PENETRATION_DEPTH_RANGE_M,
        LAND_BREEZE_TYPICAL_SPEED_RANGE_KT,
        SEA_BREEZE_TYPICAL_PENETRATION_DEPTH_RANGE_M,
        SEA_BREEZE_TYPICAL_SPEED_RANGE_KT,
    )

    assert SEA_BREEZE_TYPICAL_SPEED_RANGE_KT == (10.0, 15.0)
    assert LAND_BREEZE_TYPICAL_SPEED_RANGE_KT == (5.0, 10.0)
    sea_low, sea_high = SEA_BREEZE_TYPICAL_PENETRATION_DEPTH_RANGE_M
    land_low, land_high = LAND_BREEZE_TYPICAL_PENETRATION_DEPTH_RANGE_M
    assert sea_high > land_high  # real sea breeze penetrates further inland than the land breeze offshore


def test_mistral_speeds_are_real_and_ordered():
    from awci.knowledge.meteorology.local_winds import (
        MISTRAL_GUST_SPEED_MINIMUM_EXCEEDED_KMH,
        MISTRAL_TYPICAL_MEAN_SPEED_KMH_APPROX,
    )

    assert MISTRAL_TYPICAL_MEAN_SPEED_KMH_APPROX == 50.0
    assert MISTRAL_GUST_SPEED_MINIMUM_EXCEEDED_KMH == 100.0
    assert MISTRAL_GUST_SPEED_MINIMUM_EXCEEDED_KMH > MISTRAL_TYPICAL_MEAN_SPEED_KMH_APPROX


def test_foehn_reference_is_complementary_to_the_computed_formula():
    """The real, typical empirical Foehn temperature-increase range
    here is independent of and does not duplicate the real, computed
    acf.model4d.physics.mountain_physics.MountainPhysics.
    foehn_temperature() dry-adiabatic formula - both can coexist
    without overlap."""
    from acf.model4d.physics.mountain_physics import MountainPhysics
    from awci.knowledge.meteorology.local_winds import FOEHN_TYPICAL_TEMPERATURE_INCREASE_RANGE_C

    low, high = FOEHN_TYPICAL_TEMPERATURE_INCREASE_RANGE_C
    assert low == 5.0
    assert high == 10.0
    assert not hasattr(MountainPhysics, "FOEHN_TYPICAL_TEMPERATURE_INCREASE_RANGE_C")


def test_coriolis_and_geostrophic_equator_facts_are_real():
    from awci.knowledge.meteorology.local_winds import (
        CORIOLIS_FORCE_MAXIMUM_AT_POLES,
        CORIOLIS_FORCE_ZERO_AT_EQUATOR,
        GEOSTROPHIC_WIND_UNDEFINED_AT_EQUATOR,
    )

    assert CORIOLIS_FORCE_ZERO_AT_EQUATOR is True
    assert CORIOLIS_FORCE_MAXIMUM_AT_POLES is True
    assert GEOSTROPHIC_WIND_UNDEFINED_AT_EQUATOR is True


def test_kelvin_celsius_anchor_and_absolute_zero_are_real():
    from awci.knowledge.meteorology.temperature_reference import (
        ABSOLUTE_ZERO_C,
        KELVIN_ZERO_CELSIUS_OFFSET,
    )

    assert KELVIN_ZERO_CELSIUS_OFFSET == 273.15
    assert ABSOLUTE_ZERO_C == -273.15
    assert ABSOLUTE_ZERO_C == -KELVIN_ZERO_CELSIUS_OFFSET


def test_tropopause_and_stratopause_temperature_ranges_are_real_and_ordered():
    from awci.knowledge.meteorology.temperature_reference import (
        STRATOPAUSE_TEMPERATURE_RANGE_C,
        TROPOPAUSE_TEMPERATURE_RANGE_C_TEMPERATE,
    )

    trop_low, trop_high = TROPOPAUSE_TEMPERATURE_RANGE_C_TEMPERATE
    assert trop_low == -56.0
    assert trop_high == -55.0
    assert trop_low < trop_high

    strato_low, strato_high = STRATOPAUSE_TEMPERATURE_RANGE_C
    assert strato_low == -3.0
    assert strato_high == 0.0
    # Real consistency check against the existing atmosphere_composition
    # value (270 K = -3.15 degC), within this real observed range.
    from awci.knowledge.meteorology.atmosphere_composition import STRATOPAUSE_TEMPERATURE_K_APPROX

    stratopause_c = STRATOPAUSE_TEMPERATURE_K_APPROX - 273.15
    assert strato_low - 0.2 <= stratopause_c <= strato_high


def test_mesosphere_minimum_temperature_discrepancy_is_disclosed_not_silently_merged():
    """A real, disclosed discrepancy between two lavionnaire.fr pages -
    NOT merged into the existing
    atmosphere_composition.MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX."""
    from awci.knowledge.meteorology.atmosphere_composition import (
        MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX,
    )
    from awci.knowledge.meteorology.temperature_reference import (
        MESOSPHERE_MINIMUM_TEMPERATURE_RANGE_C_ALTERNATE_SOURCE,
    )

    assert MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX == -100.0
    alt_low, alt_high = MESOSPHERE_MINIMUM_TEMPERATURE_RANGE_C_ALTERNATE_SOURCE
    assert alt_low == -80.0
    assert alt_high == -73.0
    assert MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX not in (alt_low, alt_high)
    assert MESOSPHERE_MINIMUM_TEMPERATURE_C_APPROX < alt_low


def test_subsidence_inversion_altitude_ranges_are_real_and_nested():
    from awci.knowledge.meteorology.temperature_reference import (
        SUBSIDENCE_INVERSION_POSSIBLE_ALTITUDE_RANGE_FT,
        SUBSIDENCE_INVERSION_TYPICAL_ALTITUDE_RANGE_FT,
    )

    typical_low, typical_high = SUBSIDENCE_INVERSION_TYPICAL_ALTITUDE_RANGE_FT
    possible_low, possible_high = SUBSIDENCE_INVERSION_POSSIBLE_ALTITUDE_RANGE_FT
    assert typical_low == 8_000.0
    assert typical_high == 12_000.0
    assert possible_low == 5_000.0
    assert possible_high == 18_000.0
    assert possible_low <= typical_low and typical_high <= possible_high


def test_wind_chill_example_values_are_real():
    from awci.knowledge.meteorology.temperature_reference import (
        WIND_CHILL_EXAMPLE_AIR_TEMPERATURE_C,
        WIND_CHILL_EXAMPLE_PERCEIVED_TEMPERATURE_C,
        WIND_CHILL_EXAMPLE_WIND_SPEED_KMH,
    )

    assert WIND_CHILL_EXAMPLE_AIR_TEMPERATURE_C == -10.0
    assert WIND_CHILL_EXAMPLE_WIND_SPEED_KMH == 30.0
    assert WIND_CHILL_EXAMPLE_PERCEIVED_TEMPERATURE_C == -20.0
    assert WIND_CHILL_EXAMPLE_PERCEIVED_TEMPERATURE_C < WIND_CHILL_EXAMPLE_AIR_TEMPERATURE_C


def test_earth_axial_tilt_is_real():
    from awci.knowledge.meteorology.temperature_reference import EARTH_AXIAL_TILT_DEG

    assert EARTH_AXIAL_TILT_DEG == 23.27


def test_cloud_element_apparent_width_criterion_is_real_and_ordered():
    from awci.knowledge.meteorology.cloud_characteristics import (
        ALTOCUMULUS_ELEMENT_APPARENT_WIDTH_RANGE_DEG,
        CIRROCUMULUS_ELEMENT_APPARENT_WIDTH_MAXIMUM_DEG,
        STRATOCUMULUS_ELEMENT_APPARENT_WIDTH_MINIMUM_DEG,
    )

    assert CIRROCUMULUS_ELEMENT_APPARENT_WIDTH_MAXIMUM_DEG == 1.0
    ac_low, ac_high = ALTOCUMULUS_ELEMENT_APPARENT_WIDTH_RANGE_DEG
    assert ac_low == 1.0
    assert ac_high == 5.0
    assert STRATOCUMULUS_ELEMENT_APPARENT_WIDTH_MINIMUM_DEG == 5.0
    assert CIRROCUMULUS_ELEMENT_APPARENT_WIDTH_MAXIMUM_DEG == ac_low
    assert ac_high == STRATOCUMULUS_ELEMENT_APPARENT_WIDTH_MINIMUM_DEG


def test_apparent_width_criterion_genera_are_real_wmo_cloud_genus_members():
    from awci.knowledge.meteorology.clouds import CloudGenus
    from awci.knowledge.meteorology.cloud_characteristics import _APPARENT_WIDTH_CRITERION_GENERA

    assert len(_APPARENT_WIDTH_CRITERION_GENERA) == 3
    for genus in _APPARENT_WIDTH_CRITERION_GENERA:
        assert isinstance(genus, CloudGenus)
    assert CloudGenus.CIRROCUMULUS in _APPARENT_WIDTH_CRITERION_GENERA
    assert CloudGenus.ALTOCUMULUS in _APPARENT_WIDTH_CRITERION_GENERA
    assert CloudGenus.STRATOCUMULUS in _APPARENT_WIDTH_CRITERION_GENERA


def test_convective_bubble_and_pileus_and_psc_facts_are_real():
    from awci.knowledge.meteorology.cloud_characteristics import (
        CONVECTIVE_BUBBLE_TYPICAL_DIAMETER_DESCRIPTION,
        PILEUS_FORMATION_VERTICAL_SPEED_RANGE_KMH,
        POLAR_STRATOSPHERIC_CLOUD_TYPICAL_EXTENT_KM_APPROX,
    )

    assert "several hundred metres" in CONVECTIVE_BUBBLE_TYPICAL_DIAMETER_DESCRIPTION
    low, high = PILEUS_FORMATION_VERTICAL_SPEED_RANGE_KMH
    assert low == 20.0
    assert high == 50.0
    assert POLAR_STRATOSPHERIC_CLOUD_TYPICAL_EXTENT_KM_APPROX == 100.0
