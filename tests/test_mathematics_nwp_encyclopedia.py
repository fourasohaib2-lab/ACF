"""
Unit test suite for science.encyclopedia.mathematics_nwp's compute_func entries
(Étape 3 encyclopedia literature-verification pass).

REWRITTEN: the "vector_calculus_spherical" entry's compute_func was wired to
calculate_finite_difference_gradient - the exact same generic 1D Cartesian
centered-difference function used by the unrelated "finite_difference_schemes"
entry. That function takes a flat f_values/dx pair and has no latitude input
at all, so it could never apply the cos(phi) metric factor the spherical
divergence equation requires - a genuine formula-mismatch bug, the same class
as the doppler_velocity_dealiasing bug fixed earlier this session. Replaced
with a genuine calculate_spherical_divergence implementation.
"""

import math

import numpy as np

from acf.science.encyclopedia.mathematics_nwp import (
    calculate_departure_point_semi_lagrangian,
    calculate_finite_difference_gradient,
    calculate_spherical_divergence,
)
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_spherical_divergence_is_zero_for_nondivergent_solid_rotation():
    """
    CORRECTED: the textbook non-divergent test case for the spherical
    divergence operator - solid-body zonal rotation u = U0*cos(phi), v = 0 -
    must have zero divergence everywhere. The previous (wrong) compute_func
    had no way to even accept this input shape, let alone honor it.
    """
    lat_deg = np.linspace(-80, 80, 33)
    lon_deg = np.linspace(0, 350, 36)
    dlon_deg = lon_deg[1] - lon_deg[0]

    u = np.tile((20.0 * np.cos(np.radians(lat_deg)))[:, None], (1, len(lon_deg)))
    v = np.zeros_like(u)

    div = calculate_spherical_divergence(u, v, lat_deg, dlon_deg)

    assert div.shape == u.shape
    assert np.max(np.abs(div)) < 1e-9


def test_spherical_divergence_is_nonzero_for_a_convergent_field():
    lat_deg = np.linspace(-80, 80, 33)
    lon_deg = np.linspace(0, 350, 36)
    dlon_deg = lon_deg[1] - lon_deg[0]

    u = np.tile(np.sin(np.radians(lon_deg))[None, :] * 10.0, (len(lat_deg), 1))
    v = np.zeros_like(u)

    div = calculate_spherical_divergence(u, v, lat_deg, dlon_deg)

    assert np.max(np.abs(div)) > 1e-9


def test_vector_calculus_spherical_entry_no_longer_uses_the_unrelated_1d_gradient():
    """The registered compute_func must be the real spherical-divergence function, not the 1D Cartesian one."""
    entry = EncyclopediaRegistry._entries["vector_calculus_spherical"]
    assert entry.compute_func is calculate_spherical_divergence
    assert entry.compute_func is not calculate_finite_difference_gradient


def test_finite_difference_gradient_still_correct_for_its_own_entry():
    """finite_difference_schemes genuinely uses calculate_finite_difference_gradient - unchanged, still correct."""
    f_values = [0.0, 1.0, 4.0, 9.0, 16.0]  # x^2 samples at x=0..4
    grad = calculate_finite_difference_gradient(f_values, dx=1.0)
    # d(x^2)/dx = 2x -> centered differences of x^2 are exact at 2,4,6
    assert grad[1] == 2.0  # (4-0)/2
    assert grad[2] == 4.0  # (9-1)/2
    assert grad[3] == 6.0  # (16-4)/2


def test_semi_lagrangian_departure_point_unchanged_and_correct():
    x_dep = calculate_departure_point_semi_lagrangian(x_arrival=100.0, u_arrival=10.0, dt=2.0)
    assert math.isclose(x_dep, 80.0)
