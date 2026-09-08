"""
Tests for acf.aviation.icao.metar_decoder.METARDecoder.

These use METAR strings that are DIFFERENT from the one pre-existing
test in tests/test_operational_flight_meteorology.py, specifically to
prove this is real parsing and not a coincidental match against a
hard-coded stub (see metar_decoder.py's module docstring for the
history of the bug this replaces).
"""

import pytest

from acf.aviation.icao.metar_decoder import METARDecoder


def test_basic_metar_matches_all_fields():
    r = METARDecoder.decode("LFPG 020800Z 24018G28KT 9999 -RA BKN025 18/12 Q1015")
    assert r.icao_code == "LFPG"
    assert r.day == 2 and r.hour == 8 and r.minute == 0
    assert r.wind_direction_deg == 240
    assert r.wind_speed_kt == 18.0
    assert r.wind_gust_kt == 28.0
    # "9999" is the WMO/ICAO sentinel for "visibility >= 10 km", not a
    # literal 9999 m measurement - see decode()'s own NOTE.
    assert r.visibility_m == 10000.0
    assert r.present_weather == ["-RA"]
    assert r.cloud_layers == [{"coverage": "BKN", "base_ft": 2500, "type": None}]
    assert r.temperature_c == 18.0
    assert r.dewpoint_c == 12.0
    assert r.qnh_hpa == 1015.0


def test_cavok_and_variable_wind_and_nosig():
    r = METARDecoder.decode("EGLL 021200Z VRB02KT CAVOK 15/10 Q1020 NOSIG")
    assert r.wind_variable_direction is True
    assert r.wind_direction_deg is None
    assert r.wind_speed_kt == 2.0
    assert r.cavok is True
    assert r.visibility_m == 10000.0
    assert r.trend == "NOSIG"


def test_statute_miles_negative_temp_inhg_altimeter():
    r = METARDecoder.decode("KJFK 021151Z 28015G22KT 10SM FEW250 M03/M08 A2992")
    assert r.visibility_m == pytest.approx(16093.44)
    assert r.temperature_c == -3.0
    assert r.dewpoint_c == -8.0
    # A2992 (29.92 inHg) is close to standard sea-level pressure (1013.25 hPa).
    assert r.qnh_hpa == pytest.approx(1013.2, abs=0.1)


def test_fractional_statute_miles_severe_weather_cb():
    r = METARDecoder.decode("KORD 021253Z 22025G35KT 1/2SM +TSRA OVC008CB 24/22 Q1002")
    assert r.visibility_m == pytest.approx(804.672)
    assert r.present_weather == ["+TSRA"]
    assert r.cloud_layers[0]["coverage"] == "OVC"
    assert r.cloud_layers[0]["base_ft"] == 800
    assert r.cloud_layers[0]["type"] == "CB"


def test_auto_flag_and_calm_wind():
    r = METARDecoder.decode("LFPO 021000Z AUTO 00000KT 9999 SCT030 12/08 Q1018")
    assert r.is_auto is True
    assert r.wind_direction_deg == 0
    assert r.wind_speed_kt == 0.0


def test_wind_variable_direction_group():
    r = METARDecoder.decode("LFPG 020800Z 24010KT 210V270 9999 NSC 20/10 Q1015")
    assert r.wind_variable_from_deg == 210
    assert r.wind_variable_to_deg == 270
    assert r.cloud_layers == []


def test_multiple_cloud_layers():
    r = METARDecoder.decode("LFPG 020800Z 24010KT 9999 FEW015 SCT025 BKN040 20/10 Q1015")
    assert len(r.cloud_layers) == 3
    assert r.cloud_layers[0]["coverage"] == "FEW"
    assert r.cloud_layers[1]["coverage"] == "SCT"
    assert r.cloud_layers[2]["coverage"] == "BKN"


def test_vertical_visibility():
    r = METARDecoder.decode("LFPG 020800Z 24010KT 0400 FG VV002 05/05 Q1020")
    assert r.vertical_visibility_ft == 200
    assert r.present_weather == ["FG"]


def test_mps_wind_unit_converted_to_knots():
    r = METARDecoder.decode("UUEE 020800Z 24010MPS 9999 NSC 05/00 Q1010")
    assert r.wind_speed_kt == pytest.approx(10.0 * 1.94384)


def test_rvr_group_parsed():
    r = METARDecoder.decode("LFPG 020800Z 24010KT 0350 R27L/0400 FG VV002 03/03 Q1015")
    assert len(r.rvr) == 1
    assert r.rvr[0]["runway"] == "27L"
    assert r.rvr[0]["value_m"] == 400.0


def test_tempo_trend_detected():
    r = METARDecoder.decode("LFPG 020800Z 24010KT 9999 SCT030 20/10 Q1015 TEMPO 4000 SHRA")
    assert r.trend == "TEMPO"


def test_missing_station_id_raises():
    with pytest.raises(ValueError):
        METARDecoder.decode("020800Z 24010KT 9999 NSC 20/10 Q1015")


def test_missing_wind_group_raises():
    with pytest.raises(ValueError):
        METARDecoder.decode("LFPG 020800Z 9999 NSC 20/10 Q1015")


def test_empty_string_raises():
    with pytest.raises(ValueError):
        METARDecoder.decode("")


def test_icao_met_decoder_is_not_the_old_hardcoded_stub():
    """
    Regression guard: ICAOMetDecoder.decode_metar() used to return the
    exact same METARData (wind 240/18G28, vis 9999, -RA, BKN025,
    18/12, Q1015) for ANY input. A completely different real METAR
    must now decode to genuinely different values.
    """
    from acf.aviation.icao.products import ICAOMetDecoder

    result = ICAOMetDecoder.decode_metar("KDEN 021751Z 09005KT 10SM SKC 28/M02 A3015")

    assert result.icao_code == "KDEN"
    assert result.wind_direction_deg == 90
    assert result.wind_speed_kt == 5.0
    assert result.wind_gust_kt is None  # old stub always returned 28
    assert result.temperature_c == 28.0  # old stub always returned 18.0
    assert result.dewpoint_c == -2.0  # old stub always returned 12.0
    assert result.qnh_hpa == pytest.approx(1021.0, abs=0.5)  # old stub always returned 1015.0
    assert result.cloud_layers == []  # SKC -> no layers; old stub always returned BKN025
