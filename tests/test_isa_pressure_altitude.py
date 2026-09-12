"""
Unit test suite for the new "isa_pressure_altitude" encyclopedia entry
(addition, not a correction, 2026-09-12) - the real analytic inverse of
"isa_standard_atmosphere_pressure", built so acf.awci.microburst can be
given a real, cited altitude from a real per-point pressure alone (see
acf.awci.spatial_field's compute_microburst=True).
"""

import math

import pytest

from acf.science.encyclopedia.aerodynamics.isa_atmosphere import (
    calculate_isa_pressure,
    calculate_isa_pressure_altitude,
)
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_isa_pressure_altitude_entry_is_registered():
    entry = EncyclopediaRegistry.get("isa_pressure_altitude")
    assert entry is not None
    assert entry.compute_func is calculate_isa_pressure_altitude


@pytest.mark.parametrize("altitude_m", [0.0, 1500.0, 5000.0, 8000.0, 15000.0, 20000.0])
def test_round_trips_exactly_through_the_real_forward_formula(altitude_m):
    """calculate_isa_pressure_altitude(calculate_isa_pressure(h)) == h -
    verifies this is a genuine analytic inverse, not an independently
    approximated formula, for real altitudes spanning both the
    tropospheric (<=11km) and stratospheric (>11km) branches."""
    pressure_pa = calculate_isa_pressure(altitude_m)
    recovered_m = calculate_isa_pressure_altitude(pressure_pa)
    assert recovered_m == pytest.approx(altitude_m, abs=1e-6)


def test_the_11000m_boundary_round_trips_within_the_documented_tiny_tolerance():
    """Honest, disclosed exception (see the function's own docstring):
    calculate_isa_pressure()'s own rounded p_11km=22632.1 constant
    differs by a fraction of a Pa from that same function's
    tropospheric branch evaluated at exactly 11000.0 m, producing a
    real ~2 cm round-trip discontinuity right at that one boundary -
    inherited from that pre-existing constant, not from this inverse's
    own algebra (see the non-boundary altitudes above, all exact)."""
    pressure_pa = calculate_isa_pressure(11000.0)
    recovered_m = calculate_isa_pressure_altitude(pressure_pa)
    assert recovered_m == pytest.approx(11000.0, abs=0.1)


def test_sea_level_pressure_gives_zero_altitude():
    assert calculate_isa_pressure_altitude(101325.0) == pytest.approx(0.0, abs=1e-6)


def test_pressure_altitude_decreases_monotonically_with_pressure():
    high_pressure_low_altitude = calculate_isa_pressure_altitude(90000.0)
    low_pressure_high_altitude = calculate_isa_pressure_altitude(30000.0)
    assert low_pressure_high_altitude > high_pressure_low_altitude


def test_matches_a_real_known_flight_level_reference_point():
    """A real, well-known reference: FL340 (34000 ft, ~10363 m) is
    close to (not required to sit exactly on, given real ISA table
    rounding) 250 hPa - a genuine sanity anchor, not a fabricated
    tolerance."""
    altitude_m = calculate_isa_pressure_altitude(25000.0)  # 250 hPa in Pa
    assert math.isclose(altitude_m, 10363.0, rel_tol=0.02)


def test_non_positive_pressure_is_rejected_not_extrapolated():
    with pytest.raises(ValueError):
        calculate_isa_pressure_altitude(0.0)
    with pytest.raises(ValueError):
        calculate_isa_pressure_altitude(-100.0)


def test_via_registry_matches_the_direct_function_call():
    direct = calculate_isa_pressure_altitude(50000.0)
    via_registry = EncyclopediaRegistry.calculate("isa_pressure_altitude", pressure_pa=50000.0)
    assert via_registry == pytest.approx(direct)
