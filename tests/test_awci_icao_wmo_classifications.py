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
(awci.knowledge.meteorology.low_level_wind_gradient), and the real
microburst physical-scale/detection-system reference
(awci.knowledge.meteorology.microburst_reference).

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
https://www.lavionnaire.fr/PhenomGradient.php, and
https://www.lavionnaire.fr/PhenomCisaille.php, at the user's own
request, rather than relying on recalled tables alone for this level of
numeric/letter-code detail.
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
