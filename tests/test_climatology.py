"""
Tests for acf.science.climatology.
"""

import pytest

from acf.science.climatology import ClimatologicalRecord, Climatology, HeatColdWave


def test_percentile_value_median():
    assert Climatology.percentile_value([1, 2, 3, 4, 5], 50.0) == pytest.approx(3.0)


def test_percentile_value_min_max():
    sample = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert Climatology.percentile_value(sample, 0.0) == pytest.approx(10.0)
    assert Climatology.percentile_value(sample, 100.0) == pytest.approx(50.0)


def test_percentile_value_interpolation():
    # matches numpy.percentile's default 'linear' method
    assert Climatology.percentile_value([1, 2, 3, 4], 25.0) == pytest.approx(1.75)


def test_percentile_value_empty_raises():
    with pytest.raises(ValueError):
        Climatology.percentile_value([], 50.0)


def test_percentile_value_invalid_range():
    with pytest.raises(ValueError):
        Climatology.percentile_value([1, 2, 3], 150.0)


def test_z_score_at_mean_is_zero():
    sample = [10.0, 20.0, 30.0]
    assert Climatology.z_score(20.0, sample) == pytest.approx(0.0)


def test_z_score_known_value():
    sample = [10.0, 20.0, 30.0]  # mean=20, population std = sqrt(((10)^2+0+(10)^2)/3) = sqrt(66.67) ~ 8.165
    z = Climatology.z_score(30.0, sample)
    assert z == pytest.approx((30.0 - 20.0) / 8.16497, rel=1e-3)


def test_z_score_zero_variance_raises():
    with pytest.raises(ValueError):
        Climatology.z_score(5.0, [5.0, 5.0, 5.0])


def test_z_score_insufficient_sample_raises():
    with pytest.raises(ValueError):
        Climatology.z_score(5.0, [5.0])


def test_climatological_record_convenience_methods():
    rec = ClimatologicalRecord(variable="Tmax", station_id="DAAG", values=[10.0, 20.0, 30.0, 40.0, 50.0])
    assert rec.percentile_value(50.0) == pytest.approx(30.0)
    assert rec.z_score(30.0) == pytest.approx(0.0, abs=1.0)  # sanity, not exact


def test_detect_spells_finds_qualifying_run():
    values = [1, 1, 5, 5, 5, 5, 5, 5, 1, 1]  # 6 consecutive 5's (indices 2-7)
    spells = HeatColdWave.detect_spells(values, threshold=3.0, above_threshold=True, min_consecutive_days=6)
    assert spells == [(2, 7)]


def test_detect_spells_rejects_short_run():
    values = [1, 1, 5, 5, 5, 1, 1]  # only 3 consecutive 5's, need 6
    spells = HeatColdWave.detect_spells(values, threshold=3.0, above_threshold=True, min_consecutive_days=6)
    assert spells == []


def test_detect_spells_run_to_end_of_series():
    values = [1, 1, 5, 5, 5, 5, 5, 5]  # run extends to the last index
    spells = HeatColdWave.detect_spells(values, threshold=3.0, above_threshold=True, min_consecutive_days=6)
    assert spells == [(2, 7)]


def test_detect_spells_cold_spell_below_threshold():
    values = [10, 10, 1, 1, 1, 1, 1, 1, 10]
    spells = HeatColdWave.detect_spells(values, threshold=5.0, above_threshold=False, min_consecutive_days=6)
    assert spells == [(2, 7)]


def test_wsdi_day_count_matches_etccdi_definition():
    # Climatology sample centered so that 90th percentile is ~35.
    climatology = list(range(10, 41))  # 10..40, 90th percentile = 37
    daily_tmax = [20.0] * 5 + [38.0] * 7 + [20.0] * 5  # 7-day warm spell above ~37
    wsdi = HeatColdWave.wsdi_day_count(daily_tmax, climatology)
    assert wsdi == 7


def test_wsdi_day_count_zero_when_no_qualifying_spell():
    climatology = list(range(10, 41))
    daily_tmax = [20.0] * 5 + [38.0] * 3 + [20.0] * 5  # only 3 days, need 6
    wsdi = HeatColdWave.wsdi_day_count(daily_tmax, climatology)
    assert wsdi == 0


def test_csdi_day_count_matches_etccdi_definition():
    climatology = list(range(10, 41))  # 10th percentile = 13
    daily_tmin = [25.0] * 5 + [5.0] * 6 + [25.0] * 5  # 6-day cold spell below ~13
    csdi = HeatColdWave.csdi_day_count(daily_tmin, climatology)
    assert csdi == 6
