"""
Unit test suite for aviation/icao/airmet_decoder.py - added 2026-09-12
during the ICAO/WMO compliance audit. AIRMET had NO decoder anywhere in
this codebase before this (confirmed via grep); this replicates
sigmet_decoder.py's own real-parsing structure and test discipline
(distinct FIRs/phenomena to prove genuine per-message parsing, not a
lucky match against one hard-coded case).
"""

import pytest

from acf.aviation.icao.airmet_decoder import AIRMETDecoder

_LFFF_TURB = "LFFF AIRMET 1 VALID 020800/021200 LFPW-\nLFFF PARIS FIR MOD TURB OBS AT 0800Z N OF N48 FL050/FL100 MOV E 15KT NC="
_KZAK_ICE = (
    "KZAK AIRMET 2 VALID 021200/021600 KZAK-\n"
    "KZAK OAKLAND OCEANIC FIR MOD ICE FCST AT 1200Z S OF N30 FL020/FL080 MOV NE 20KT INTSF="
)
_EGTT_WIND = "EGTT AIRMET 3 VALID 021400/021800 EGRR-\nEGTT LONDON FIR SFC WIND OBS SFC/FL050 STNR NC="
_RJJJ_MTOBSC = "RJJJ AIRMET 4 VALID 020300/020700 RJTD-\nRJJJ FUKUOKA FIR MT OBSC OBS AT 0300Z SFC/FL100 MOV S 10KT NC="


def test_header_fields():
    r = AIRMETDecoder.decode(_LFFF_TURB)
    assert r.fir_code == "LFFF"
    assert r.sequence_number == "1"
    assert r.issuing_center == "LFPW"
    assert r.valid_from_day == 2 and r.valid_from_hour == 8 and r.valid_from_minute == 0
    assert r.valid_until_day == 2 and r.valid_until_hour == 12 and r.valid_until_minute == 0


def test_moderate_turbulence_with_fl_range_and_movement():
    r = AIRMETDecoder.decode(_LFFF_TURB)
    assert r.phenomenon == "MOD TURB"
    assert r.is_observed is True
    assert r.observed_or_forecast_hour == 8
    assert r.flight_level_bottom == 50
    assert r.flight_level_top == 100
    assert r.movement_dir == "E"
    assert r.movement_speed_kt == 15.0
    assert r.is_stationary is False


def test_moderate_icing_forecast():
    r = AIRMETDecoder.decode(_KZAK_ICE)
    assert r.fir_code == "KZAK"
    assert r.phenomenon == "MOD ICE"
    assert r.is_observed is False  # FCST, not OBS
    assert r.observed_or_forecast_hour == 12
    assert r.flight_level_bottom == 20
    assert r.flight_level_top == 80
    assert r.movement_dir == "NE"
    assert r.movement_speed_kt == 20.0


def test_surface_wind_stationary_from_surface():
    r = AIRMETDecoder.decode(_EGTT_WIND)
    assert r.fir_code == "EGTT"
    assert r.phenomenon == "SFC WIND"
    assert r.flight_level_bottom == 0  # SFC
    assert r.flight_level_top == 50
    assert r.is_stationary is True
    assert r.movement_dir is None


def test_mountain_obscuration():
    r = AIRMETDecoder.decode(_RJJJ_MTOBSC)
    assert r.fir_code == "RJJJ"
    assert r.phenomenon == "MT OBSC"
    assert r.flight_level_bottom == 0
    assert r.flight_level_top == 100
    assert r.movement_dir == "S"
    assert r.movement_speed_kt == 10.0


def test_all_four_examples_produce_genuinely_distinct_results():
    reports = [AIRMETDecoder.decode(t) for t in (_LFFF_TURB, _KZAK_ICE, _EGTT_WIND, _RJJJ_MTOBSC)]
    fir_codes = {r.fir_code for r in reports}
    phenomena = {r.phenomenon for r in reports}
    assert len(fir_codes) == 4
    assert len(phenomena) == 4


def test_location_text_is_preserved_verbatim_not_structurally_parsed():
    r = AIRMETDecoder.decode(_LFFF_TURB)
    assert "N OF N48" in r.location_text
    assert r.location_text.startswith("LFFF PARIS FIR")


def test_raises_on_missing_header():
    with pytest.raises(ValueError, match="AIRMET header"):
        AIRMETDecoder.decode("This is not an AIRMET at all.")


def test_raises_on_empty_text():
    with pytest.raises(ValueError, match="empty"):
        AIRMETDecoder.decode("")


def test_no_crash_on_truncated_body_missing_fields_stay_none():
    r = AIRMETDecoder.decode("LFFF AIRMET 1 VALID 020800/021200 LFPW- LFFF PARIS FIR MOD TURB")
    assert r.phenomenon == "MOD TURB"
    assert r.flight_level_top is None
    assert r.movement_dir is None
    assert r.is_stationary is False
