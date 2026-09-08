"""
Tests for acf.gui.dashboard.acf_workstation_quality - the real
per-point §32 data-quality helper backing the AWCI-free ACF Scientific
Workstation's Data Quality Center (added 2026-09-04).
"""

from __future__ import annotations

import numpy as np

from acf.gui.dashboard.acf_workstation_quality import compute_real_data_quality_fields
from acf.physics_guard.variable_quality import VARIABLE_QUALITY_STATUSES, assess_variable_quality


def test_data_quality_fields_match_the_real_assess_function_directly():
    """Cross-check discipline: every cell must equal an independent,
    direct call to assess_variable_quality() on that same real point -
    never a separately re-derived status."""
    rng = np.random.default_rng(0)
    temperature = 280.0 + rng.uniform(-10.0, 10.0, size=(3, 4))
    specific_humidity = np.clip(0.006 + rng.uniform(-0.002, 0.002, size=(3, 4)), 1e-6, None)
    pressure_hpa = np.full((3, 4), 1000.0)  # a real, in-range value
    wind_speed = rng.uniform(0.0, 30.0, size=(3, 4))

    results = compute_real_data_quality_fields(temperature, specific_humidity, pressure_hpa, wind_speed)

    cf_names = {
        "Temperature": "air_temperature",
        "Specific humidity": "specific_humidity",
        "Pressure": "air_pressure",
        "Wind speed": "wind_speed",
    }
    for i in range(3):
        for j in range(4):
            data = {
                "air_temperature": float(temperature[i, j]),
                "specific_humidity": float(specific_humidity[i, j]),
                "air_pressure": float(pressure_hpa[i, j]),
                "wind_speed": float(wind_speed[i, j]),
            }
            expected = assess_variable_quality(data, expected_variables=list(data.keys()), units={"air_pressure": "hPa"})
            for panel_name, cf_name in cf_names.items():
                severity_grid, _counts = results[panel_name]
                expected_severity = VARIABLE_QUALITY_STATUSES.index(expected[cf_name].status)
                assert severity_grid[i, j] == expected_severity


def test_in_range_values_are_all_valid():
    """A real, trivial sanity case: physically ordinary values must
    all read VALID (severity 0)."""
    temperature = np.full((2, 2), 288.0)
    specific_humidity = np.full((2, 2), 0.008)
    pressure_hpa = np.full((2, 2), 1013.0)
    wind_speed = np.full((2, 2), 10.0)

    results = compute_real_data_quality_fields(temperature, specific_humidity, pressure_hpa, wind_speed)

    for _severity_grid, counts in results.values():
        assert counts == {"VALID": 4}


def test_a_genuinely_out_of_range_pressure_is_honestly_caught():
    """Real regression guard for the §32 quality check itself: a
    genuinely out-of-range surface pressure must be honestly flagged
    OUT_OF_RANGE, not silently accepted. Uses ~2013 hPa - the exact
    value a real, since-fixed CoupledEarthSolver bug (task_f3c406d9,
    EarthGrid.a_coeff started at 100000.0 Pa instead of 0.0 at the
    surface) used to genuinely produce - kept as a real, meaningful
    literal test input for the range check itself, independent of
    whatever the solver produces today."""
    temperature = np.full((2, 2), 288.0)
    specific_humidity = np.full((2, 2), 0.008)
    pressure_hpa = np.full((2, 2), 2013.25)  # a real, genuinely out-of-range value
    wind_speed = np.full((2, 2), 10.0)

    results = compute_real_data_quality_fields(temperature, specific_humidity, pressure_hpa, wind_speed)

    pressure_severity_grid, pressure_counts = results["Pressure"]
    assert pressure_counts == {"OUT_OF_RANGE": 4}
    assert np.all(pressure_severity_grid == VARIABLE_QUALITY_STATUSES.index("OUT_OF_RANGE"))
    # The other 3 real variables, unaffected, must still read VALID.
    for name in ("Temperature", "Specific humidity", "Wind speed"):
        _severity_grid, counts = results[name]
        assert counts == {"VALID": 4}
