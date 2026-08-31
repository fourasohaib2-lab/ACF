"""
Tests for acf.science.diagnostics.
"""

from acf.science.diagnostics import SituationDiagnosis


def test_stable_fair_regime_no_alerts():
    d = SituationDiagnosis.diagnose()
    assert d.weather_regime == "Stable/Fair"
    assert d.alerts == []
    assert d.highest_alert_level() == "None"


def test_severe_convective_regime_from_threat_level():
    d = SituationDiagnosis.diagnose(cape_j_kg=3000.0, threat_level="Extreme tornado potential")
    assert d.weather_regime == "Severe Convective"
    assert d.highest_alert_level() == "Severe"
    assert any("CAPE extrême" in a.message for a in d.alerts)


def test_poor_visibility_regime():
    d = SituationDiagnosis.diagnose(visibility_m=500.0)
    assert d.weather_regime == "Poor Visibility"
    assert any(a.category == "visibility" for a in d.alerts)


def test_heavy_rain_regime():
    d = SituationDiagnosis.diagnose(precipitation_rate_mm_h=20.0)
    assert d.weather_regime == "Heavy Rain"
    assert any(a.category == "precipitation" and a.level == "Warning" for a in d.alerts)


def test_showery_convective_regime_from_cape():
    d = SituationDiagnosis.diagnose(cape_j_kg=1500.0)
    assert d.weather_regime == "Showery/Convective"


def test_light_rain_regime():
    d = SituationDiagnosis.diagnose(precipitation_rate_mm_h=1.0, cape_j_kg=0.0)
    assert d.weather_regime == "Light Rain"


def test_wind_alerts():
    d_warning = SituationDiagnosis.diagnose(wind_speed_m_s=18.0)
    assert any(a.category == "wind" and a.level == "Warning" for a in d_warning.alerts)

    d_severe = SituationDiagnosis.diagnose(wind_speed_m_s=10.0, wind_gust_m_s=30.0)
    assert any(a.category == "wind" and a.level == "Severe" for a in d_severe.alerts)


def test_highest_alert_level_picks_max_severity():
    d = SituationDiagnosis.diagnose(cape_j_kg=1200.0, wind_speed_m_s=20.0, precipitation_rate_mm_h=60.0)
    assert d.highest_alert_level() == "Severe"


def test_explanation_always_present():
    d = SituationDiagnosis.diagnose()
    assert len(d.explanation) >= 1
    assert "Stable/Fair" in d.explanation[0]
