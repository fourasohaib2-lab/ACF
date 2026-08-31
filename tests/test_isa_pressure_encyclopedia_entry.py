"""
Unit test suite for the new "isa_standard_atmosphere_pressure" encyclopedia
entry (Étape 3 encyclopedia literature-verification pass - an addition, not a
correction).

calculate_isa_pressure() was already defined in aerodynamics/isa_atmosphere.py
and already directly unit-tested (test_global_scientific_encyclopedia.py), but
was never wired to any EncyclopediaEntry or registered - "isa_standard_atmosphere_model"
only ever exposed its sibling calculate_isa_temperature() as a compute_func,
even though the entry's own equation documents both T(z) and p(z). Registered
as its own entry per the golden rule (every real, verified law gets
registered) rather than left orphaned.
"""

import math

from acf.science.encyclopedia.aerodynamics.isa_atmosphere import calculate_isa_pressure
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_isa_pressure_entry_is_registered():
    entry = EncyclopediaRegistry.get("isa_standard_atmosphere_pressure")
    assert entry is not None
    assert entry.compute_func is calculate_isa_pressure


def test_isa_pressure_entry_matches_standard_isa_table_values():
    # Standard ICAO ISA reference table values (Pa), all within 0.1%.
    reference = {0.0: 101325.0, 5000.0: 54048.0, 11000.0: 22632.1, 15000.0: 12044.6}
    for altitude_m, expected_pa in reference.items():
        result = EncyclopediaRegistry.calculate("isa_standard_atmosphere_pressure", altitude_m=altitude_m)
        assert math.isclose(result, expected_pa, rel_tol=1e-3)


def test_isa_pressure_decreases_monotonically_with_altitude():
    p_sea_level = EncyclopediaRegistry.calculate("isa_standard_atmosphere_pressure", altitude_m=0.0)
    p_cruise = EncyclopediaRegistry.calculate("isa_standard_atmosphere_pressure", altitude_m=11000.0)
    p_high = EncyclopediaRegistry.calculate("isa_standard_atmosphere_pressure", altitude_m=15000.0)
    assert p_sea_level > p_cruise > p_high
