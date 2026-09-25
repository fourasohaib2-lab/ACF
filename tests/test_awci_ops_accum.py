"""Accumulated IFS fields differenced between steps; OLR effective temperature; snow; condensate."""

import numpy as np

from acf.awci.ops.accum import (
    STEFAN_BOLTZMANN,
    accumulated_layers,
    column_condensate,
    effective_emission_temperature_k,
    freezing_precip_mm,
    interval_amount_mm,
    olr_w_m2,
    snow_depth_cm,
)


def test_olr_from_ttr_difference() -> None:
    olr = olr_w_m2(np.array(-240.0 * 3 * 3600 * 2), np.array(-240.0 * 3 * 3600), 3.0)
    assert np.isclose(olr, 240.0)
    assert np.isnan(olr_w_m2(np.array(0.0), np.array(0.0), 3.0))  # no emission = no data, not 0 K


def test_effective_temperature_255k_for_240_w_m2() -> None:
    assert STEFAN_BOLTZMANN == 5.670374419e-8
    assert np.isclose(effective_emission_temperature_k(np.array(240.0)), 255.064, atol=1e-3)


def test_interval_amount_clips_packing_noise() -> None:
    assert np.isclose(interval_amount_mm(np.array(0.0035), np.array(0.0010)), 2.5)
    assert interval_amount_mm(np.array(0.0010), np.array(0.0010000001)) == 0.0


def test_snow_depth_from_water_equivalent_and_density() -> None:
    assert np.isclose(snow_depth_cm(np.array(0.03), np.array(300.0)), 10.0)
    assert snow_depth_cm(np.array(0.0), np.array(100.0)) == 0.0
    assert np.isnan(snow_depth_cm(np.array(0.01), np.array(0.0)))


def test_freezing_precip_requires_freezing_type_at_both_ends() -> None:
    now, prev = np.array([0.004, 0.004, 0.004]), np.array([0.001, 0.001, 0.001])
    out = freezing_precip_mm(now, prev, np.array([3.0, 12.0, 1.0]), np.array([3.0, 3.0, 3.0]))
    np.testing.assert_allclose(out, [3.0, 3.0, 0.0])


def test_column_condensate_non_negative() -> None:
    np.testing.assert_allclose(column_condensate(np.array([30.5, 20.0]), np.array([30.0, 20.1])), [0.5, 0.0])


def test_accumulated_layers_nan_without_previous_step() -> None:
    sfc = {k: np.ones((2, 2)) for k in ("ttr", "sf", "tp", "ptype")}
    out = accumulated_layers(sfc, None, None)
    assert set(out) == {"cloud_top_teff_k", "snowfall_mm", "freezing_precip_mm"}
    assert all(np.isnan(v).all() for v in out.values())
