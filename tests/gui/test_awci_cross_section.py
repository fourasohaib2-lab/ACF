"""
Tests for acf.gui.dashboard.awci_cross_section - in particular
_hpa_to_ft()'s extrapolation fix (found 2026-09-02 while wiring the
cross-section panel to real CoupledEarthSolver data: real pressures can
exceed the table's 1013 hPa top entry, and the old clamping behavior
collapsed multiple distinct real levels onto the same y=0 ft).
"""

from acf.gui.dashboard.awci_cross_section import _hpa_to_ft


def test_hpa_to_ft_within_table_matches_known_points():
    assert _hpa_to_ft(1013.0) == 0.0
    assert _hpa_to_ft(850.0) == 4800.0
    assert _hpa_to_ft(150.0) == 44600.0


def test_hpa_to_ft_interpolates_between_table_points():
    mid = _hpa_to_ft(925.0)  # halfway between 1013 and 850
    assert 0.0 < mid < 4800.0


def test_hpa_to_ft_out_of_range_high_pressure_extrapolates_not_clamps():
    """
    CORRECTED: pressures above 1013 hPa (real CoupledEarthSolver output
    can reach ~2013 hPa - see vertical_field.py's own docstring on its
    idealized pressure scale) used to all clamp to the same 0.0 ft.
    """
    low = _hpa_to_ft(1100.0)
    high = _hpa_to_ft(2000.0)
    assert low != 0.0
    assert high != 0.0
    assert low != high
    assert high < low  # higher pressure -> lower (more negative) altitude


def test_hpa_to_ft_real_solver_profile_produces_distinct_monotonic_altitudes():
    """
    Regression test for the exact failure found via a real screenshot:
    a real 20-native-level CoupledEarthSolver pressure profile must map
    to 20 distinct, monotonically increasing altitudes - not 10 of them
    colliding at 0.0 ft.
    """
    levels_hpa = [
        2013.2, 1907.3, 1801.4, 1695.5, 1589.6, 1483.7, 1377.8, 1271.9, 1166.0, 1060.1,
        954.2, 848.3, 742.4, 636.4, 530.5, 424.6, 318.7, 212.8, 106.9, 1.0,
    ]
    altitudes = [_hpa_to_ft(p) for p in levels_hpa]

    assert len(set(altitudes)) == len(altitudes)
    assert all(altitudes[i] < altitudes[i + 1] for i in range(len(altitudes) - 1))


def test_hpa_to_ft_out_of_range_low_pressure_extrapolates():
    very_high_altitude = _hpa_to_ft(1.0)
    assert very_high_altitude > 44600.0
