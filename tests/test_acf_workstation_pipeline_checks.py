"""
Tests for acf.gui.dashboard.acf_workstation_pipeline_checks - the real,
Qt-free QC/consistency checks behind the ACF Scientific Workstation's
own "ACF Pipeline Monitor" (Phase 32, 2026-09-05).
"""

from __future__ import annotations

import numpy as np

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_pipeline_checks import (
    run_real_derivation_consistency_check,
    run_real_range_qc,
)


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_derivation_consistency_check_passes_on_a_genuine_real_volume():
    """compute_real_complexity_volume() itself derives wind_speed_volume
    as sqrt(u^2+v^2) and pressure_volume_hpa as a strictly-positive
    Pa->hPa conversion - the real check must find both true."""
    status, detail = run_real_derivation_consistency_check(_real_volume())
    assert status == "OK"
    assert "sqrt" in detail


def test_derivation_consistency_check_catches_a_real_broken_wind_speed():
    volume = _real_volume()
    volume["wind_speed_volume"] = volume["wind_speed_volume"] + 1000.0  # genuinely break the derivation

    status, detail = run_real_derivation_consistency_check(volume)

    assert status == "FAIL"
    assert "wind_speed_volume" in detail


def test_derivation_consistency_check_catches_a_real_non_positive_pressure():
    volume = _real_volume()
    volume["pressure_volume_hpa"] = volume["pressure_volume_hpa"].copy()
    volume["pressure_volume_hpa"][0, 0, 0] = -5.0  # genuinely break the derivation

    status, detail = run_real_derivation_consistency_check(volume)

    assert status == "FAIL"
    assert "pressure_volume_hpa" in detail


def test_range_qc_reports_a_real_documented_violation_honestly():
    """Real, reproducible finding: every real MODEL_CONFIGS grid's own
    top model level genuinely reaches ~1 hPa - below
    OPERATIONAL_RANGES's own documented tropospheric-only lower bound
    (10 hPa). The check must report this honestly, never silently pass."""
    volume = _real_volume()
    assert float(np.min(volume["pressure_volume_hpa"])) < 10.0  # real, current solver behavior

    status, detail = run_real_range_qc(volume)

    assert status == "WARN"
    assert "air_pressure" in detail


def test_range_qc_passes_when_every_real_field_is_genuinely_in_range():
    volume = _real_volume()
    # Real, deliberately-in-range synthetic override so the check itself
    # (not the solver's own real stratosphere-reaching top level) is
    # what's being exercised here.
    volume["pressure_volume_hpa"] = np.full_like(volume["pressure_volume_hpa"], 850.0)

    status, detail = run_real_range_qc(volume)

    assert status == "OK"
    assert "within" in detail
