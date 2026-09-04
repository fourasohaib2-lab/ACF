"""
Tests for acf.gui.dashboard.acf_workstation_microphysics - the real
precipitation-phase/wet-bulb helper backing the AWCI-free ACF
Scientific Workstation's Microphysics Lab (added 2026-09-04).
"""

from __future__ import annotations

import numpy as np

from acf.awci.hydrometeor_phase import PHASE_SEVERITY, compute_real_hydrometeor_phase_at_point
from acf.gui.dashboard.acf_workstation_microphysics import compute_real_hydrometeor_phase_fields


def test_hydrometeor_phase_fields_match_the_real_point_function_directly():
    """Cross-check discipline: every cell must equal an independent,
    direct call to compute_real_hydrometeor_phase_at_point() on that
    same real point - never a separately re-derived formula."""
    rng = np.random.default_rng(0)
    temperature = 270.0 + rng.uniform(-15.0, 15.0, size=(4, 5))
    specific_humidity = np.clip(0.006 + rng.uniform(-0.003, 0.003, size=(4, 5)), 1e-6, None)
    pressure_hpa = np.full((4, 5), 950.0)

    phase_severity, wet_bulb_c = compute_real_hydrometeor_phase_fields(temperature, specific_humidity, pressure_hpa)

    for i in range(4):
        for j in range(5):
            expected = compute_real_hydrometeor_phase_at_point(
                float(temperature[i, j]), float(specific_humidity[i, j]), float(pressure_hpa[i, j])
            )
            assert expected["is_real_data"] is True
            assert phase_severity[i, j] == expected["phase_severity"]
            assert wet_bulb_c[i, j] == expected["wet_bulb_c"]


def test_phase_severity_values_are_the_real_disclosed_ordinal_range():
    """phase_severity must always be one of PHASE_SEVERITY's own real,
    disclosed values - never an invented intermediate number."""
    temperature = np.array([[300.0, 260.0], [268.0, 275.0]])
    specific_humidity = np.array([[0.015, 0.001], [0.004, 0.006]])
    pressure_hpa = np.full((2, 2), 1000.0)

    phase_severity, _wet_bulb_c = compute_real_hydrometeor_phase_fields(temperature, specific_humidity, pressure_hpa)

    real_values = set(PHASE_SEVERITY.values())
    for value in phase_severity.flatten():
        assert value in real_values
