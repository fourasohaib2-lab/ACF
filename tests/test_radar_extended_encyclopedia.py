"""
Unit test suite for science.encyclopedia.radar_extended's QPE compute_func fix
(Étape 3 encyclopedia literature-verification pass).

REWRITTEN: the "qpe_quantitative_precipitation_estimation" entry's
compute_func used to be calculate_rain_rate_from_z directly - a real,
correct instantaneous rain-rate formula (mm/h), but not what the entry
itself documents: its own equation is an explicit time accumulation
(R_accumulated = sum_t R*dt) and its declared units are "QPE: mm" (an
accumulated depth), not mm/h. Added calculate_qpe_accumulation(), which
multiplies the instantaneous rate by a duration to produce a genuine
accumulated depth in mm, matching the entry's own documentation.
"""

import math

from acf.science.encyclopedia.radar_extended import (
    calculate_qpe_accumulation,
    calculate_rain_rate_from_z,
)
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def test_qpe_accumulation_is_rate_times_duration():
    rate = calculate_rain_rate_from_z(z_dbz=40.0)
    accumulated = calculate_qpe_accumulation(z_dbz=40.0, duration_hours=3.0)
    assert math.isclose(accumulated, rate * 3.0)


def test_qpe_accumulation_defaults_to_one_hour_for_backward_compatibility():
    """The default duration_hours=1.0 keeps existing rate-shaped callers numerically unchanged."""
    rate = calculate_rain_rate_from_z(z_dbz=40.0)
    accumulated = calculate_qpe_accumulation(z_dbz=40.0)
    assert math.isclose(accumulated, rate)


def test_qpe_accumulation_zero_for_nonpositive_duration():
    assert calculate_qpe_accumulation(z_dbz=40.0, duration_hours=0.0) == 0.0
    assert calculate_qpe_accumulation(z_dbz=40.0, duration_hours=-1.0) == 0.0


def test_qpe_entry_wired_to_the_accumulation_function_not_the_bare_rate():
    entry = EncyclopediaRegistry._entries["qpe_quantitative_precipitation_estimation"]
    assert entry.compute_func is calculate_qpe_accumulation
    assert entry.compute_func is not calculate_rain_rate_from_z


def test_qpe_registry_calculate_scales_with_duration():
    r_1h = EncyclopediaRegistry.calculate("qpe_quantitative_precipitation_estimation", z_dbz=40.0, duration_hours=1.0)
    r_24h = EncyclopediaRegistry.calculate(
        "qpe_quantitative_precipitation_estimation", z_dbz=40.0, duration_hours=24.0
    )
    assert math.isclose(r_24h, r_1h * 24.0)
