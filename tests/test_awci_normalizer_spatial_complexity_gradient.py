"""
Tests for Normalizer.normalize_spatial_complexity_gradient() - added
2026-09-13 at the user's explicit request to visually match the
reference mockup's "Complexity Index" card on ACF Workstation's
Overview page (see acf_workstation_overview_landing.py's own module
docstring for the full context and why this reuses the same
HYPOTHESIS-level, disclosed normalization pattern every other
Normalizer method already uses, rather than a new kind of fabrication).
"""

from __future__ import annotations

import pytest

from acf.awci.normalizer import Normalizer


def test_normalize_spatial_complexity_gradient_matches_its_own_disclosed_5_k_per_100km_range():
    assert Normalizer.normalize_spatial_complexity_gradient(2.5) == pytest.approx(0.5)
    assert Normalizer.normalize_spatial_complexity_gradient(0.0) == 0.0
    assert Normalizer.normalize_spatial_complexity_gradient(5.0) == pytest.approx(1.0)


def test_normalize_spatial_complexity_gradient_clips_out_of_range_values():
    assert Normalizer.normalize_spatial_complexity_gradient(50.0) == 1.0  # clipped
    assert Normalizer.normalize_spatial_complexity_gradient(-1.0) == 0.0  # clipped
