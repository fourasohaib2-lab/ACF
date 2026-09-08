"""
Tests for acf.science.visibility.
"""

import pytest

from acf.science.visibility import FogRisk, ICAOCategory, Koschmieder


def test_koschmieder_known_relation():
    v = Koschmieder.visibility(extinction_coefficient_per_m=0.001)
    assert v == pytest.approx(3912.0)


def test_koschmieder_invalid_extinction():
    with pytest.raises(ValueError):
        Koschmieder.visibility(0.0)


def test_extinction_from_lwc_positive():
    sigma = Koschmieder.extinction_coefficient_from_lwc(liquid_water_content_kg_m3=0.0002, effective_radius_m=5e-6)
    assert sigma > 0


def test_visibility_from_lwc_denser_fog_reduces_visibility():
    v_light = Koschmieder.visibility_from_lwc(liquid_water_content_kg_m3=0.0001, effective_radius_m=5e-6)
    v_dense = Koschmieder.visibility_from_lwc(liquid_water_content_kg_m3=0.001, effective_radius_m=5e-6)
    assert v_dense < v_light


def test_icao_cat_i():
    assert ICAOCategory.classify(decision_height_m=60.0, rvr_m=600.0) == "CAT I"


def test_icao_cat_ii():
    assert ICAOCategory.classify(decision_height_m=45.0, rvr_m=350.0) == "CAT II"


def test_icao_cat_iiia():
    assert ICAOCategory.classify(decision_height_m=20.0, rvr_m=200.0) == "CAT IIIa"


def test_icao_cat_iiib():
    assert ICAOCategory.classify(decision_height_m=10.0, rvr_m=100.0) == "CAT IIIb"


def test_icao_cat_iiic_no_dh_no_rvr():
    assert ICAOCategory.classify(decision_height_m=None, rvr_m=None) == "CAT IIIc"


def test_icao_below_minima():
    assert ICAOCategory.classify(decision_height_m=60.0, rvr_m=100.0) == "Below CAT III minima"


def test_fog_risk_daytime_is_low():
    assert (
        FogRisk.radiation_fog_risk(
            wind_speed_m_s=1.0, cloud_cover_fraction=0.1, dewpoint_depression_k=1.0, is_nighttime=False
        )
        == "Low"
    )


def test_fog_risk_ideal_nighttime_conditions_high():
    risk = FogRisk.radiation_fog_risk(
        wind_speed_m_s=1.5, cloud_cover_fraction=0.1, dewpoint_depression_k=1.0, is_nighttime=True
    )
    assert risk == "High"


def test_fog_risk_windy_clear_night_lower_risk():
    risk = FogRisk.radiation_fog_risk(
        wind_speed_m_s=8.0, cloud_cover_fraction=0.1, dewpoint_depression_k=1.0, is_nighttime=True
    )
    assert risk in ("Low", "Moderate")


def test_fog_risk_invalid_cloud_cover():
    with pytest.raises(ValueError):
        FogRisk.radiation_fog_risk(
            wind_speed_m_s=1.0, cloud_cover_fraction=1.5, dewpoint_depression_k=1.0, is_nighttime=True
        )
