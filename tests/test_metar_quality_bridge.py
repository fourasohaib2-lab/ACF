"""
Tests for acf.aviation.icao.metar_decoder.metar_report_quality() - real
per-variable quality status (docs/ACF_MASTER_PROMPT.md section 32) for
a real, decoded METAR/SPECI report. Explicit user request: "le but est
de brancher acf et awci avec des vrais station pour nous rendre des
vrai reponse instantanément" - closes the quality-flagging half of
that loop for real live station data.
"""

from __future__ import annotations

from acf.aviation.icao.metar_decoder import METARDecoder, metar_report_quality


def test_normal_metar_reports_valid_for_every_present_variable():
    report = METARDecoder.decode("LFPG 020800Z 24018G28KT 9999 -RA BKN025 18/12 Q1015")
    quality = metar_report_quality(report)

    assert quality["air_temperature"].status == "VALID"
    assert quality["dewpoint_temperature"].status == "VALID"
    assert quality["air_pressure"].status == "VALID"
    assert quality["wind_speed"].status == "VALID"


def test_only_fields_the_report_actually_carries_are_assessed():
    """A report with no altimeter group present must not fabricate
    MISSING for a variable never confirmed expected - the real
    decoded string simply has no Q#### group."""
    report = METARDecoder.decode("LFPO 021000Z AUTO 00000KT 9999 SCT030 12/08")
    quality = metar_report_quality(report)
    assert "air_pressure" not in quality  # no Q#### group in this string


def test_celsius_native_unit_matches_a_direct_kelvin_range_check():
    from acf.physics_guard.variable_quality import assess_variable_quality

    report = METARDecoder.decode("LFPG 020800Z 24018G28KT 9999 -RA BKN025 18/12 Q1015")
    quality = metar_report_quality(report)

    direct = assess_variable_quality(
        {"air_temperature": 18.0}, expected_variables=["air_temperature"], units={"air_temperature": "degC"}
    )
    assert quality["air_temperature"].status == direct["air_temperature"].status


def test_extreme_temperature_is_flagged_out_of_range():
    report = METARDecoder.decode("KXXX 021151Z 28015KT 10SM FEW250 99/50 A2992")
    quality = metar_report_quality(report)
    assert quality["air_temperature"].status == "OUT_OF_RANGE"


def test_wind_speed_knots_converted_correctly_stays_valid():
    # 18 kt is a real, unremarkable surface wind - must stay VALID once
    # converted to m/s against the real wind_speed range.
    report = METARDecoder.decode("LFPG 020800Z 24018KT 9999 NSC 15/10 Q1015")
    quality = metar_report_quality(report)
    assert quality["wind_speed"].status == "VALID"


def test_dewpoint_above_temperature_would_be_physical_inconsistency():
    """A real, constructed inconsistency (decode() itself won't produce
    an impossible dewpoint from real station text, so this exercises
    the bridge's own consistency-check wiring directly against a
    METARReport with the field overridden post-decode)."""
    report = METARDecoder.decode("LFPG 020800Z 24018KT 9999 NSC 15/10 Q1015")
    report.dewpoint_c = 25.0  # now above temperature_c=15.0 - a genuine physical impossibility
    quality = metar_report_quality(report)
    assert quality["air_temperature"].status == "PHYSICAL_INCONSISTENCY"
    assert quality["dewpoint_temperature"].status == "PHYSICAL_INCONSISTENCY"
