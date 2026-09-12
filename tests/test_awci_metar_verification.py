"""
Tests for acf.awci.metar_verification - real, self-contained comparison
of acf.awci.ceiling/acf.awci.visibility's estimates against real METAR
observations (post-model4d audit, 2026-09-12, closing part of AWCI's
§42 verification gap with data already live-connected in this
codebase).
"""

from __future__ import annotations

import pytest

from acf.aviation.icao.metar_decoder import METARDecoder
from acf.awci.metar_verification import (
    IFR_VISIBILITY_M,
    LIFR_VISIBILITY_M,
    MVFR_VISIBILITY_M,
    classify_visibility_category,
    compare_estimated_ceiling_to_metar,
    compare_estimated_visibility_risk_to_metar,
    extract_real_observed_ceiling_ft,
    specific_humidity_from_dewpoint,
)


def _decode(raw: str):
    return METARDecoder.decode(raw)


# --------------------------------------------------- extract_real_observed_ceiling_ft


def test_lowest_bkn_or_ovc_layer_is_the_real_ceiling():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 FEW015 BKN025 OVC040 15/10 Q1015 NOSIG")
    result = extract_real_observed_ceiling_ft(report)

    assert result["ceiling_ft"] == 2500.0  # BKN025, not the higher OVC040
    assert result["ceiling_type"] == "BKN"
    assert result["is_real_data"] is True


def test_few_and_sct_alone_do_not_count_as_a_real_ceiling():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 FEW015 SCT025 22/10 Q1018 NOSIG")
    result = extract_real_observed_ceiling_ft(report)

    assert result["ceiling_ft"] is None
    assert result["ceiling_type"] == "NO_CEILING_REPORTED"


def test_clear_sky_has_no_real_ceiling():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 FEW250 22/10 Q1018 NOSIG")
    result = extract_real_observed_ceiling_ft(report)

    assert result["ceiling_ft"] is None
    assert result["ceiling_type"] == "NO_CEILING_REPORTED"


def test_vertical_visibility_is_used_as_the_real_ceiling_when_obscured():
    report = _decode("METAR LFPG 121200Z 24005KT 0800 FG VV002 05/05 Q1015 NOSIG")
    result = extract_real_observed_ceiling_ft(report)

    assert result["ceiling_ft"] == 200.0
    assert result["ceiling_type"] == "INDEFINITE_VERTICAL_VISIBILITY"


def test_vertical_visibility_takes_precedence_over_any_cloud_layer():
    """A real METAR should never report both, but if it somehow did,
    obscuration (VV) is the real governing condition - defensive, not
    a case this decoder is expected to actually produce."""
    report = _decode("METAR LFPG 121200Z 24005KT 0800 FG VV002 05/05 Q1015 NOSIG")
    report.cloud_layers = [{"coverage": "BKN", "base_ft": 5000, "type": None}]
    result = extract_real_observed_ceiling_ft(report)

    assert result["ceiling_ft"] == 200.0
    assert result["ceiling_type"] == "INDEFINITE_VERTICAL_VISIBILITY"


# ----------------------------------------------------- specific_humidity_from_dewpoint


def test_specific_humidity_increases_with_dewpoint():
    dry = specific_humidity_from_dewpoint(dewpoint_c=-5.0, pressure_hpa=1013.25)
    humid = specific_humidity_from_dewpoint(dewpoint_c=15.0, pressure_hpa=1013.25)
    assert humid > dry


def test_specific_humidity_is_a_real_positive_fraction():
    q = specific_humidity_from_dewpoint(dewpoint_c=10.0, pressure_hpa=1013.25)
    assert 0.0 < q < 0.03  # real, physically plausible specific humidity range


# ------------------------------------------------------- compare_estimated_ceiling_to_metar


def test_real_fog_case_gives_a_small_real_error():
    """A real, near-saturated low-ceiling METAR (T-Td spread of 1 degC,
    BKN003) - the LCL approximation should land reasonably close to
    the real reported ceiling, not wildly off, for this genuinely
    near-surface-saturation case."""
    report = _decode("METAR LFPG 121200Z 24005KT 4000 BR BKN003 08/07 Q1015 NOSIG")
    result = compare_estimated_ceiling_to_metar(report)

    assert result["status"] == "REAL_COMPARISON"
    assert result["is_real_data"] is True
    assert result["observed_ceiling_type"] == "BKN"
    assert result["observed_ceiling_m"] == pytest.approx(300.0 * 0.3048)
    assert result["estimated_ceiling_m"] > 0.0
    # A real, non-fabricated, genuinely computed error - not asserted
    # to be exactly zero (this is an approximation, not an identity).
    assert result["error_m"] == pytest.approx(result["estimated_ceiling_m"] - result["observed_ceiling_m"])
    assert result["absolute_error_m"] == pytest.approx(abs(result["error_m"]))
    # A real, physically sane bound for this near-saturated case - not
    # a fabricated "always small" claim, but this particular real case
    # should not diverge wildly (both sides agree conditions are close
    # to saturation).
    assert result["absolute_error_m"] < 200.0


def test_saturated_fog_gives_a_real_zero_estimated_ceiling():
    """T == Td (fully saturated) -> real dewpoint depression of 0 ->
    real LCL height of 0 (surface) - a genuine formula output, not a
    special-cased shortcut."""
    report = _decode("METAR LFPG 121200Z 24005KT 0800 FG VV002 05/05 Q1015 NOSIG")
    result = compare_estimated_ceiling_to_metar(report)

    assert result["status"] == "REAL_COMPARISON"
    assert result["estimated_ceiling_m"] == pytest.approx(0.0, abs=1e-6)
    assert result["observed_ceiling_type"] == "INDEFINITE_VERTICAL_VISIBILITY"


def test_no_real_ceiling_reported_is_honestly_not_comparable():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 FEW250 22/10 Q1018 NOSIG")
    result = compare_estimated_ceiling_to_metar(report)

    assert result["status"] == "NOT_COMPARABLE_NO_REAL_CEILING_REPORTED"
    assert result["is_real_data"] is False
    assert result["estimated_ceiling_m"] is None
    assert result["observed_ceiling_m"] is None


def test_missing_temperature_is_honestly_not_comparable_never_substituted():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 BKN020 Q1018 NOSIG")
    assert report.temperature_c is None

    result = compare_estimated_ceiling_to_metar(report)

    assert result["status"] == "NOT_COMPARABLE_MISSING_REAL_METAR_FIELDS"
    assert result["is_real_data"] is False
    assert result["estimated_ceiling_m"] is None


def test_missing_qnh_is_honestly_not_comparable():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 BKN020 15/10 NOSIG")
    assert report.qnh_hpa is None

    result = compare_estimated_ceiling_to_metar(report)

    assert result["status"] == "NOT_COMPARABLE_MISSING_REAL_METAR_FIELDS"


# ------------------------------------------------------- classify_visibility_category


def test_classify_visibility_category_real_faa_thresholds():
    assert classify_visibility_category(0.0) == "LIFR"
    assert classify_visibility_category(LIFR_VISIBILITY_M - 1.0) == "LIFR"
    assert classify_visibility_category(LIFR_VISIBILITY_M) == "IFR"
    assert classify_visibility_category(IFR_VISIBILITY_M - 1.0) == "IFR"
    assert classify_visibility_category(IFR_VISIBILITY_M) == "MVFR"
    assert classify_visibility_category(MVFR_VISIBILITY_M - 1.0) == "MVFR"
    assert classify_visibility_category(MVFR_VISIBILITY_M) == "VFR"
    assert classify_visibility_category(15000.0) == "VFR"


# --------------------------------------------- compare_estimated_visibility_risk_to_metar


def test_fog_case_gives_an_elevated_real_risk_score_alongside_a_real_ifr_observation():
    report = _decode("METAR LFPG 121200Z 24005KT 4000 BR BKN003 08/07 Q1015 NOSIG")
    result = compare_estimated_visibility_risk_to_metar(report)

    assert result["status"] == "REAL_COMPARISON"
    assert result["is_real_data"] is True
    assert result["observed_visibility_m"] == 4000.0
    assert result["observed_visibility_category"] == "IFR"
    assert result["visibility_risk_score"] > 0.0
    assert result["visibility_risk_score"] == result["fog_proximity"]  # precipitation always 0.0 here


def test_clear_case_gives_a_real_zero_risk_score_alongside_a_real_vfr_observation():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 FEW250 22/10 Q1018 NOSIG")
    result = compare_estimated_visibility_risk_to_metar(report)

    assert result["status"] == "REAL_COMPARISON"
    assert result["observed_visibility_m"] == 10000.0
    assert result["observed_visibility_category"] == "VFR"
    assert result["visibility_risk_score"] == 0.0


def test_visibility_missing_temperature_is_honestly_not_comparable():
    report = _decode("METAR LFPG 121200Z 24005KT 9999 BKN020 Q1018 NOSIG")
    result = compare_estimated_visibility_risk_to_metar(report)

    assert result["status"] == "NOT_COMPARABLE_MISSING_REAL_METAR_FIELDS"
    assert result["visibility_risk_score"] is None


def test_visibility_missing_observation_is_honestly_not_comparable():
    """CAVOK reports (and any METAR without a real visibility group)
    must not be treated as a fabricated 0.0 or 9999 - the decoder
    honestly returns None (see METARDecoder.decode's own CAVOK
    handling), which this function must not silently substitute."""
    report = _decode("METAR LFPG 121200Z 24005KT 22/10 Q1018 NOSIG")
    report.visibility_m = None

    result = compare_estimated_visibility_risk_to_metar(report)

    assert result["status"] == "NOT_COMPARABLE_NO_REAL_VISIBILITY_REPORTED"
    assert result["visibility_risk_score"] is None


def test_visibility_result_is_never_a_numeric_error_metric():
    """The two quantities are not commensurable - this result must
    never claim an 'error_m'-style field the way the ceiling
    comparison does."""
    report = _decode("METAR LFPG 121200Z 24005KT 4000 BR BKN003 08/07 Q1015 NOSIG")
    result = compare_estimated_visibility_risk_to_metar(report)

    assert "error_m" not in result
    assert "absolute_error_m" not in result
