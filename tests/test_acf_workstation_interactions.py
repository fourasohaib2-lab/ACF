"""
Tests for acf.gui.dashboard.acf_workstation_interactions - the real,
statistically-justified pointwise correlation helper backing the
AWCI-free ACF Scientific Workstation's Interaction Engine (added
2026-09-04, explicit master-spec rule docs/ACF_MASTER_PROMPT.md §22:
"Ne pas inventer arbitrairement interaction = A x B sans justification
physique ou statistique").
"""

from __future__ import annotations

import numpy as np

from acf.gui.dashboard.acf_workstation_interactions import compute_real_local_interaction


def test_local_interaction_spatial_mean_matches_numpy_corrcoef():
    """Cross-check discipline: the real spatial mean of
    local_interaction must equal numpy's own real, standard Pearson
    correlation coefficient exactly - proving this is the real,
    standard statistic, not a separately re-derived formula."""
    rng = np.random.default_rng(0)
    field_a = rng.uniform(0.0, 10.0, size=(6, 7))
    field_b = 2.0 * field_a + rng.normal(0.0, 1.0, size=(6, 7))

    local_interaction, pearson_r = compute_real_local_interaction(field_a, field_b)

    expected = np.corrcoef(field_a.flatten(), field_b.flatten())[0, 1]
    assert np.isclose(pearson_r, expected)
    assert np.isclose(np.nanmean(local_interaction), expected)


def test_local_interaction_is_perfect_for_a_perfectly_linear_relationship():
    """A real, trivial sanity case: B is an exact positive linear
    function of A - real correlation must be exactly 1.0."""
    field_a = np.array([[1.0, 2.0], [3.0, 4.0]])
    field_b = 5.0 * field_a + 3.0

    _local_interaction, pearson_r = compute_real_local_interaction(field_a, field_b)

    assert np.isclose(pearson_r, 1.0)


def test_local_interaction_is_perfectly_negative_for_an_inverse_relationship():
    field_a = np.array([[1.0, 2.0], [3.0, 4.0]])
    field_b = -2.0 * field_a + 1.0

    _local_interaction, pearson_r = compute_real_local_interaction(field_a, field_b)

    assert np.isclose(pearson_r, -1.0)


def test_local_interaction_is_honestly_nan_for_a_zero_variance_field():
    """A real, degenerate case - a perfectly uniform field has no real
    variance to correlate against - must be honestly NaN, never a
    fabricated 0 or 1."""
    field_a = np.full((3, 3), 42.0)  # zero real variance
    field_b = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

    local_interaction, pearson_r = compute_real_local_interaction(field_a, field_b)

    assert np.isnan(pearson_r)
    assert np.all(np.isnan(local_interaction))


def test_local_interaction_is_near_zero_for_independent_random_fields():
    """A real, large-sample sanity case: two independently-drawn
    random fields should show a real correlation close to 0."""
    rng = np.random.default_rng(1)
    field_a = rng.normal(0.0, 1.0, size=(50, 50))
    field_b = rng.normal(0.0, 1.0, size=(50, 50))

    _local_interaction, pearson_r = compute_real_local_interaction(field_a, field_b)

    assert abs(pearson_r) < 0.1
