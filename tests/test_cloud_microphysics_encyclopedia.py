"""
Unit test suite for three cloud-microphysics compute_func precision fixes found
during the Étape 3 encyclopedia literature-verification pass:

1. bergeron_findeisen_diff(): ice saturation vapor pressure coefficients
   corrected from (22.58, 273.16) to the standard Alduchov & Eskridge (1996)
   fit (22.587, 273.86) - 273.16 (the triple point of water) was a suspicious
   substitute for the fitted 273.86.
2. calculate_homogeneous_nucleation_rate(): cutoff corrected from -35°C to
   -38°C, aligning the compute_func with this entry's own equation/
   description text (both already stated -38°C; only the code and the
   "limitations" field disagreed).
3. calculate_hallett_mossop_splintering(): efficiency previously peaked at
   -5.5°C (the geometric midpoint of the [-8, -3] window) despite the
   comment and literature (Hallett & Mossop 1974) stating the true peak is
   at -5°C. Replaced with an asymmetric piecewise-linear efficiency that
   genuinely peaks at -5°C.
"""

import math

from acf.science.encyclopedia.cloud_microphysics.cloud_classification import bergeron_findeisen_diff
from acf.science.encyclopedia.cloud_physics.cloud_physics import calculate_homogeneous_nucleation_rate
from acf.science.encyclopedia.cloud_physics.wmo_cloud_taxonomy import calculate_hallett_mossop_splintering


def test_bergeron_findeisen_uses_standard_ice_formula_coefficients():
    # e_i(T) = 611.21 * exp(22.587*T / (T+273.86)) - spot check at -20°C against direct computation.
    temp_c = -20.0
    e_w = 611.2 * math.exp((17.67 * temp_c) / (temp_c + 243.5))
    e_i_expected = 611.21 * math.exp((22.587 * temp_c) / (temp_c + 273.86))
    assert math.isclose(bergeron_findeisen_diff(temp_c), e_w - e_i_expected, rel_tol=1e-9)


def test_bergeron_findeisen_positive_in_mixed_phase_range():
    assert bergeron_findeisen_diff(-15.0) > 0.0


def test_homogeneous_nucleation_cutoff_matches_entry_documentation():
    """CORRECTED: cutoff was -35°C, inconsistent with this entry's own equation/description text (-38°C)."""
    assert calculate_homogeneous_nucleation_rate(-37.0) == 0.0
    assert calculate_homogeneous_nucleation_rate(-38.0) == 0.0
    assert calculate_homogeneous_nucleation_rate(-39.0) > 0.0


def test_hallett_mossop_peak_is_genuinely_at_minus_5c():
    """
    CORRECTED: used to peak at -5.5°C (window midpoint) instead of the
    literature-established -5°C (Hallett & Mossop 1974; "near -5°C" within
    the [-8, -3] window).
    """
    rate_at_peak = calculate_hallett_mossop_splintering(-5.0, rime_rate_mg_s=10.0)
    assert rate_at_peak == 350.0 * 10.0  # efficiency == 1.0 exactly at the true peak

    for other_temp in (-8.0, -7.0, -6.0, -4.0, -3.5, -3.0):
        assert calculate_hallett_mossop_splintering(other_temp, rime_rate_mg_s=10.0) < rate_at_peak

    # Zero at both window boundaries.
    assert calculate_hallett_mossop_splintering(-8.0, rime_rate_mg_s=10.0) == 0.0
    assert calculate_hallett_mossop_splintering(-3.0, rime_rate_mg_s=10.0) == 0.0

    # Outside the [-8, -3] window: no splintering.
    assert calculate_hallett_mossop_splintering(-15.0, rime_rate_mg_s=10.0) == 0.0
    assert calculate_hallett_mossop_splintering(-1.0, rime_rate_mg_s=10.0) == 0.0
