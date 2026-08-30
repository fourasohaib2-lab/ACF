import pytest

from acf.science.severe_weather import SevereWeather


def test_summary():

    result = SevereWeather.summary(
        cape=2500,
        cin=-40,
        shear=28,
        srh=320,
    )

    assert result["cape"] == 2500
    assert result["cin"] == -40
    assert result["bulk_shear"] == 28
    assert result["srh"] == 320


def test_summary_adds_composite_indices_without_breaking_legacy_keys():
    result = SevereWeather.summary(cape=2500, cin=-40, shear=28, srh=320)
    # legacy keys untouched (already covered by test_summary, re-asserted for clarity)
    assert set(["cape", "cin", "bulk_shear", "srh"]).issubset(result.keys())
    # new keys present
    assert "ehi" in result and "scp" in result and "stp" in result and "threat_level" in result
    assert result["stp"] is None  # no lcl_m supplied
    assert result["ehi"] > 0
    assert result["scp"] > 0
    assert isinstance(result["threat_level"], str)


def test_summary_with_lcl_computes_stp():
    result = SevereWeather.summary(cape=2500, cin=-40, shear=28, srh=320, lcl_m=900)
    assert result["stp"] is not None
    assert result["stp"] > 0


def test_energy_helicity_index_known_value():
    # EHI = CAPE * SRH / 160000 (Hart & Korotky, 1991)
    assert SevereWeather.energy_helicity_index(cape=1600, srh=160) == pytest.approx(1.6)


def test_energy_helicity_index_zero_srh():
    assert SevereWeather.energy_helicity_index(cape=3000, srh=0) == 0.0


def test_supercell_composite_parameter_capped_terms():
    # effective_bulk_shear > 20 -> ebwd_term capped at 1.0
    # mucin > -40 -> cin_term = 1.0
    scp = SevereWeather.supercell_composite_parameter(
        mucape=2000, effective_srh=200, effective_bulk_shear=25, mucin=-10
    )
    expected = (2000 / 1000.0) * (200 / 50.0) * 1.0 * 1.0
    assert scp == pytest.approx(expected)


def test_supercell_composite_parameter_low_shear_is_zero():
    scp = SevereWeather.supercell_composite_parameter(
        mucape=2000, effective_srh=200, effective_bulk_shear=5, mucin=-10
    )
    assert scp == 0.0


def test_stp_fixed_lcl_below_1000_caps_at_one():
    stp = SevereWeather.significant_tornado_parameter_fixed(
        sbcape=1500, sblcl_m=800, srh_1km=150, shear_6km=20
    )
    expected = (1500 / 1500.0) * 1.0 * (150 / 150.0) * (20 / 20.0)
    assert stp == pytest.approx(expected)


def test_stp_fixed_lcl_above_2000_zeroes_out():
    stp = SevereWeather.significant_tornado_parameter_fixed(
        sbcape=2000, sblcl_m=2500, srh_1km=200, shear_6km=25
    )
    assert stp == 0.0


def test_stp_fixed_low_shear_zeroes_out():
    stp = SevereWeather.significant_tornado_parameter_fixed(
        sbcape=2000, sblcl_m=900, srh_1km=200, shear_6km=8
    )
    assert stp == 0.0


def test_stp_effective_cin_term_bounds():
    # mlcin > -50 -> cin_term = 1.0
    stp_favorable_cin = SevereWeather.significant_tornado_parameter_effective(
        mlcape=2000, mllcl_m=900, effective_srh=200, effective_bulk_shear=20, mlcin=-10
    )
    # mlcin < -200 -> cin_term = 0.0 -> whole product zero
    stp_capped_cin = SevereWeather.significant_tornado_parameter_effective(
        mlcape=2000, mllcl_m=900, effective_srh=200, effective_bulk_shear=20, mlcin=-250
    )
    assert stp_favorable_cin > 0
    assert stp_capped_cin == 0.0


def test_classify_threat_levels():
    assert SevereWeather.classify_threat(ehi=0.2, scp=0.2, stp=None) == "Low organized-severe potential"
    assert SevereWeather.classify_threat(ehi=1.5, scp=0.2, stp=None) == "Some rotational potential"
    assert SevereWeather.classify_threat(ehi=1.5, scp=1.5, stp=None) == "Supercells favored"
    assert SevereWeather.classify_threat(ehi=1.5, scp=1.5, stp=1.2) == "Significant tornado potential"
    assert SevereWeather.classify_threat(ehi=1.5, scp=1.5, stp=3.5) == "Extreme tornado potential"
