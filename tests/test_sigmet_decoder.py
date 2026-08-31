"""
Unit test suite for aviation/icao/sigmet_decoder.py — a real, best-effort
SIGMET parser replacing the previous fabricated stub (see
ICAOMetDecoder.decode_sigmet()'s NOTE in products.py for the original bug:
the identical fixed SIGMET - FIR "LFFF", phenomenon "EMBD TS", "SEV"
severity, FL100/FL380, fixed validity/movement - returned regardless of
input).

Test SIGMETs are deliberately drawn from different regions/FIRs and
phenomena (Paris embedded thunderstorms, Oakland Oceanic severe turbulence,
London severe icing, Fukuoka volcanic ash) to prove genuine per-message
parsing, not a lucky match against one hard-coded case.
"""

import pytest

from acf.aviation.icao.sigmet_decoder import SIGMETDecoder

_LFFF_TS = "LFFF SIGMET 2 VALID 020800/021200 LFPW-\nLFFF PARIS FIR EMBD TS OBS AT 0800Z N OF N50 TOP FL390 MOV E 15KT NC="
_KZAK_TURB = (
    "KZAK SIGMET 1 VALID 021200/021600 KZAK-\n"
    "KZAK OAKLAND OCEANIC FIR SEV TURB FCST AT 1200Z S OF N30 FL180/FL340 MOV NE 25KT INTSF="
)
_EGTT_ICE = "EGTT SIGMET 5 VALID 021400/021800 EGRR-\nEGTT LONDON FIR SEV ICE FCST WI 300NM OF EGLL FL050/FL150 STNR NC="
_RJJJ_VA = "RJJJ SIGMET 3 VALID 020300/020700 RJTD-\nRJJJ FUKUOKA FIR VA CLD OBS AT 0300Z SFC/FL200 MOV S 10KT NC="


def test_header_fields():
    r = SIGMETDecoder.decode(_LFFF_TS)
    assert r.fir_code == "LFFF"
    assert r.sequence_number == "2"
    assert r.issuing_center == "LFPW"
    assert r.valid_from_day == 2 and r.valid_from_hour == 8 and r.valid_from_minute == 0
    assert r.valid_until_day == 2 and r.valid_until_hour == 12 and r.valid_until_minute == 0


def test_embedded_thunderstorm_with_top_and_movement():
    r = SIGMETDecoder.decode(_LFFF_TS)
    assert r.phenomenon == "EMBD TS"
    assert r.intensity_qualifier == "EMBD"
    assert r.is_observed is True
    assert r.observed_or_forecast_hour == 8
    assert r.flight_level_top == 390
    assert r.flight_level_bottom is None
    assert r.movement_dir == "E"
    assert r.movement_speed_kt == 15.0
    assert r.is_stationary is False


def test_severe_turbulence_with_fl_range_and_forecast():
    r = SIGMETDecoder.decode(_KZAK_TURB)
    assert r.fir_code == "KZAK"
    assert r.phenomenon == "SEV TURB"
    assert r.severity == "SEV"
    assert r.is_observed is False  # FCST, not OBS
    assert r.observed_or_forecast_hour == 12
    assert r.flight_level_bottom == 180
    assert r.flight_level_top == 340
    assert r.movement_dir == "NE"
    assert r.movement_speed_kt == 25.0


def test_severe_icing_stationary():
    r = SIGMETDecoder.decode(_EGTT_ICE)
    assert r.fir_code == "EGTT"
    assert r.phenomenon == "SEV ICE"
    assert r.severity == "SEV"
    assert r.flight_level_bottom == 50
    assert r.flight_level_top == 150
    assert r.is_stationary is True
    assert r.movement_dir is None
    assert r.movement_speed_kt is None


def test_volcanic_ash_from_surface():
    r = SIGMETDecoder.decode(_RJJJ_VA)
    assert r.fir_code == "RJJJ"
    assert r.phenomenon == "VA CLD"
    assert r.flight_level_bottom == 0  # SFC
    assert r.flight_level_top == 200
    assert r.movement_dir == "S"
    assert r.movement_speed_kt == 10.0


def test_all_four_examples_produce_genuinely_distinct_results():
    """The exact original bug: every SIGMET used to decode to the identical fixed fake report."""
    reports = [SIGMETDecoder.decode(t) for t in (_LFFF_TS, _KZAK_TURB, _EGTT_ICE, _RJJJ_VA)]
    fir_codes = {r.fir_code for r in reports}
    phenomena = {r.phenomenon for r in reports}
    assert len(fir_codes) == 4
    assert len(phenomena) == 4


def test_severity_and_intensity_are_distinguished():
    """SEV/MOD (severity) and OBSC/EMBD/FRQ/SQL/ISOL/OCNL (intensity qualifier) are separate concepts."""
    r_turb = SIGMETDecoder.decode(_KZAK_TURB)
    assert r_turb.severity == "SEV"
    assert r_turb.intensity_qualifier is None

    r_ts = SIGMETDecoder.decode(_LFFF_TS)
    assert r_ts.intensity_qualifier == "EMBD"
    assert r_ts.severity is None


def test_location_text_is_preserved_verbatim_not_structurally_parsed():
    """Geographic description is genuinely free-text - preserved, not guessed at."""
    r = SIGMETDecoder.decode(_LFFF_TS)
    assert "N OF N50" in r.location_text
    assert r.location_text.startswith("LFFF PARIS FIR")


def test_raises_on_missing_header():
    with pytest.raises(ValueError, match="SIGMET header"):
        SIGMETDecoder.decode("This is not a SIGMET at all.")


def test_raises_on_empty_text():
    with pytest.raises(ValueError, match="empty"):
        SIGMETDecoder.decode("")


def test_no_crash_on_truncated_body_missing_fields_stay_none():
    """A minimal/truncated SIGMET with only FIR+phenomenon must not crash - missing fields stay None."""
    r = SIGMETDecoder.decode("LFFF SIGMET 2 VALID 020800/021200 LFPW- LFFF PARIS FIR EMBD TS")
    assert r.phenomenon == "EMBD TS"
    assert r.flight_level_top is None
    assert r.movement_dir is None
    assert r.is_stationary is False
