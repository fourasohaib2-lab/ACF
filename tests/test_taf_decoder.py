"""
Unit test suite for aviation/icao/taf_decoder.py — a real, token-based TAF
parser replacing the previous fabricated-forecast stub (see
ICAOMetDecoder.decode_taf()'s NOTE in products.py for the original bug: the
same TAF change group returned regardless of input, for ANY airport/day/
forecast).

Test TAFs are deliberately distinct from each other and from the plain
base-forecast-only example used in test_operational_flight_meteorology.py, to
prove genuine per-message parsing rather than a lucky match against one
hard-coded case.
"""

import pytest

from acf.aviation.icao.taf_decoder import TAFDecoder


def test_header_parsing():
    r = TAFDecoder.decode("TAF LFPG 020600Z 0206/0312 24015KT 9999 SCT030")
    assert r.icao_code == "LFPG"
    assert r.issue_day == 2 and r.issue_hour == 6 and r.issue_minute == 0
    assert r.valid_from_day == 2 and r.valid_from_hour == 6
    assert r.valid_until_day == 3 and r.valid_until_hour == 12
    assert not r.is_amended
    assert not r.is_corrected


def test_amd_and_cor_flags():
    r_amd = TAFDecoder.decode("TAF AMD EDDF 021105Z 0212/0318 VRB03KT CAVOK")
    assert r_amd.is_amended
    assert not r_amd.is_corrected

    r_cor = TAFDecoder.decode("TAF COR KJFK 021740Z 0218/0324 22012KT 9999 SCT250")
    assert r_cor.is_corrected
    assert not r_cor.is_amended


def test_base_forecast_wind_visibility_clouds():
    r = TAFDecoder.decode("TAF LFPG 020600Z 0206/0312 24015KT 9999 SCT030")
    assert len(r.periods) == 1
    base = r.periods[0]
    assert base.change_type == "BASE"
    assert base.wind_direction_deg == 240
    assert base.wind_speed_kt == 15.0
    assert base.wind_gust_kt is None
    # "9999" is the WMO/ICAO sentinel for "visibility >= 10 km", not a
    # literal 9999 m measurement - see _parse_wind_visibility_weather_clouds()'s NOTE.
    assert base.visibility_m == 10000.0
    assert base.cloud_layers == [{"coverage": "SCT", "base_ft": 3000, "type": None}]


def test_vrb_wind_and_cavok():
    r = TAFDecoder.decode("TAF EDDF 021105Z 0212/0318 VRB03KT CAVOK")
    base = r.periods[0]
    assert base.wind_variable is True
    assert base.wind_direction_deg is None
    assert base.wind_speed_kt == 3.0
    assert base.cavok is True
    assert base.visibility_m == 10000.0


def test_wind_gust_and_present_weather_and_cb_cloud():
    r = TAFDecoder.decode("TAF KXXX 021130Z 0212/0318 18010G25KT 4000 TSRA BKN010CB")
    base = r.periods[0]
    assert base.wind_speed_kt == 10.0
    assert base.wind_gust_kt == 25.0
    assert base.present_weather == ["TSRA"]
    assert base.cloud_layers == [{"coverage": "BKN", "base_ft": 1000, "type": "CB"}]


def test_mps_wind_unit_converted_to_knots():
    r = TAFDecoder.decode("TAF UUEE 021200Z 0212/0318 27008MPS 9999 SCT040")
    base = r.periods[0]
    assert base.wind_speed_kt == pytest.approx(8.0 * 1.94384)


def test_tempo_change_group():
    r = TAFDecoder.decode(
        "TAF LFPG 020600Z 0206/0312 24015KT 9999 SCT030 TEMPO 0206/0210 4000 SHRA BKN015CB"
    )
    assert len(r.periods) == 2
    tempo = r.periods[1]
    assert tempo.change_type == "TEMPO"
    assert tempo.probability is None
    assert tempo.from_day == 2 and tempo.from_hour == 6
    assert tempo.until_day == 2 and tempo.until_hour == 10
    assert tempo.visibility_m == 4000.0
    assert tempo.present_weather == ["SHRA"]
    assert tempo.cloud_layers == [{"coverage": "BKN", "base_ft": 1500, "type": "CB"}]


def test_becmg_change_group():
    r = TAFDecoder.decode("TAF LFPG 020600Z 0206/0312 24015KT 9999 SCT030 BECMG 0212/0214 30010KT")
    becmg = r.periods[1]
    assert becmg.change_type == "BECMG"
    assert becmg.from_day == 2 and becmg.from_hour == 12
    assert becmg.until_day == 2 and becmg.until_hour == 14
    assert becmg.wind_direction_deg == 300
    assert becmg.wind_speed_kt == 10.0


def test_prob30_tempo_combined_group():
    r = TAFDecoder.decode(
        "TAF LFPG 020600Z 0206/0312 24015KT 9999 SCT030 PROB30 TEMPO 0300/0304 0800 FG"
    )
    prob_tempo = r.periods[1]
    assert prob_tempo.change_type == "TEMPO"
    assert prob_tempo.probability == 30
    assert prob_tempo.from_day == 3 and prob_tempo.from_hour == 0
    assert prob_tempo.until_day == 3 and prob_tempo.until_hour == 4
    assert prob_tempo.visibility_m == 800.0
    assert prob_tempo.present_weather == ["FG"]


def test_prob40_standalone_group():
    r = TAFDecoder.decode("TAF KXXX 021130Z 0212/0318 18010KT 8000 PROB40 0300/0306 1600 TSRA")
    prob = r.periods[1]
    assert prob.change_type == "PROB40"
    assert prob.probability == 40
    assert prob.visibility_m == 1600.0
    assert prob.present_weather == ["TSRA"]


def test_fm_group_has_minute_precision_and_replaces_conditions():
    r = TAFDecoder.decode(
        "TAF EDDF 021105Z 0212/0318 VRB03KT CAVOK FM021800 27012G22KT 9999 SCT040 FM030600 25008KT CAVOK"
    )
    assert len(r.periods) == 3
    fm1, fm2 = r.periods[1], r.periods[2]
    assert fm1.change_type == "FM"
    assert fm1.from_day == 2 and fm1.from_hour == 18 and fm1.from_minute == 0
    assert fm1.wind_direction_deg == 270
    assert fm1.wind_speed_kt == 12.0
    assert fm1.wind_gust_kt == 22.0
    assert fm2.change_type == "FM"
    assert fm2.from_day == 3 and fm2.from_hour == 6
    assert fm2.cavok is True


def test_multiple_change_groups_all_distinct_and_in_order():
    """The exact original bug: every group used to return the identical fake TEMPO regardless of input."""
    r = TAFDecoder.decode(
        "TAF LFPG 020600Z 0206/0312 24015KT 9999 SCT030 "
        "TEMPO 0206/0210 4000 SHRA BKN015CB "
        "BECMG 0212/0214 30010KT "
        "PROB30 TEMPO 0300/0304 0800 FG"
    )
    assert [p.change_type for p in r.periods] == ["BASE", "TEMPO", "BECMG", "TEMPO"]
    # The two TEMPO periods must carry genuinely different content, not the same fabricated group.
    assert r.periods[1].visibility_m != r.periods[3].visibility_m
    assert r.periods[1].present_weather != r.periods[3].present_weather
    assert r.periods[3].probability == 30
    assert r.periods[1].probability is None


def test_rmk_section_is_truncated_not_misparsed():
    r = TAFDecoder.decode("TAF KXXX 021130Z 0212/0318 18010KT 8000 -RA SCT020 BKN040 RMK NXT FCST BY 030000Z")
    assert len(r.periods) == 1
    assert r.periods[0].present_weather == ["-RA"]


def test_vertical_visibility_group():
    r = TAFDecoder.decode("TAF KXXX 021130Z 0212/0318 18010KT 0400 FG VV002")
    base = r.periods[0]
    assert base.vertical_visibility_ft == 200
    assert base.cloud_layers == []


def test_raises_on_missing_icao_code():
    with pytest.raises(ValueError, match="ICAO station identifier"):
        TAFDecoder.decode("TAF 020600Z 0206/0312 24015KT 9999")


def test_raises_on_missing_issue_time():
    with pytest.raises(ValueError, match="issue time"):
        TAFDecoder.decode("TAF LFPG 0206/0312 24015KT 9999")


def test_raises_on_missing_validity_period():
    with pytest.raises(ValueError, match="validity period"):
        TAFDecoder.decode("TAF LFPG 020600Z 24015KT 9999")


def test_raises_on_empty_text():
    with pytest.raises(ValueError, match="empty"):
        TAFDecoder.decode("")
