"""
Tests for acf.awci.hydrometeor_phase - real per-point surface
precipitation phase and its ACF-assigned severity (docs/
ACF_MASTER_PROMPT.md section 15, candidate variable "hydrométéores").
This session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found the microphysical module used
only precipitation RATE before this, never precipitation PHASE.
"""

from __future__ import annotations

import pytest

from acf.awci.hydrometeor_phase import PHASE_SEVERITY, compute_real_hydrometeor_phase_at_point
from acf.core.exceptions import RangeError
from acf.science.precipitation import HydrometeorType
from acf.science.thermodynamics import Thermodynamics


def test_warm_humid_point_is_classified_rain():
    result = compute_real_hydrometeor_phase_at_point(
        temperature_k=293.15, specific_humidity=0.010, pressure_hpa=1000.0
    )
    assert result["phase"] == "Rain"
    assert result["phase_severity"] == pytest.approx(0.2)


def test_cold_dry_point_is_classified_snow():
    result = compute_real_hydrometeor_phase_at_point(
        temperature_k=263.15, specific_humidity=0.0015, pressure_hpa=1000.0
    )
    assert result["phase"] == "Snow"
    assert result["phase_severity"] == pytest.approx(0.5)


def test_saturated_at_freezing_is_classified_freezing_rain_or_ice_pellets():
    """0 degC surface temperature, saturated - real known transition case."""
    result = compute_real_hydrometeor_phase_at_point(
        temperature_k=273.15, specific_humidity=0.0044, pressure_hpa=1000.0
    )
    assert result["phase"] == "Freezing Rain / Ice Pellets"
    assert result["phase_severity"] == pytest.approx(1.0)


def test_saturated_just_above_freezing_is_classified_wet_snow_mix():
    """1 degC surface temperature, saturated - real known transition case."""
    result = compute_real_hydrometeor_phase_at_point(
        temperature_k=274.15, specific_humidity=0.0044, pressure_hpa=1000.0
    )
    assert result["phase"] == "Wet Snow/Mix"
    assert result["phase_severity"] == pytest.approx(0.7)


def test_matches_a_direct_composition_of_the_3_real_formulas():
    temperature_k, specific_humidity, pressure_hpa = 280.0, 0.005, 950.0

    result = compute_real_hydrometeor_phase_at_point(temperature_k, specific_humidity, pressure_hpa)

    rh_pct = Thermodynamics.calculate_relative_humidity(specific_humidity, pressure_hpa, temperature_k, is_kelvin=True)
    temp_c = temperature_k - 273.15
    wet_bulb_c = Thermodynamics.calculate_wet_bulb_temperature(temp_c, rh_pct / 100.0)
    expected_phase = HydrometeorType.classify(temp_c, wet_bulb_c)

    assert result["relative_humidity_pct"] == pytest.approx(rh_pct)
    assert result["wet_bulb_c"] == pytest.approx(wet_bulb_c)
    assert result["phase"] == expected_phase


def test_phase_severity_matches_the_phase_severity_table():
    for temperature_k, specific_humidity in [
        (293.15, 0.010),
        (263.15, 0.0015),
        (273.15, 0.0044),
        (274.15, 0.0044),
    ]:
        result = compute_real_hydrometeor_phase_at_point(temperature_k, specific_humidity, 1000.0)
        assert result["phase_severity"] == pytest.approx(PHASE_SEVERITY[result["phase"]])


def test_phase_severity_is_always_bounded_0_1():
    for temperature_k in (250.0, 260.0, 270.0, 273.15, 280.0, 300.0, 320.0):
        for specific_humidity in (0.0, 0.001, 0.005, 0.010, 0.020):
            result = compute_real_hydrometeor_phase_at_point(temperature_k, specific_humidity, 1000.0)
            assert 0.0 <= result["phase_severity"] <= 1.0


def test_is_real_data_and_status_are_honest():
    result = compute_real_hydrometeor_phase_at_point(temperature_k=290.0, specific_humidity=0.008, pressure_hpa=1000.0)
    assert result["is_real_data"] is True
    assert result["status"] == "REAL_HYDROMETEOR_PHASE_SURFACE_HEURISTIC"


def test_freezing_rain_and_ice_pellets_is_the_most_severe_real_category():
    """Real proof of the disclosed aviation-operational ordering: freezing
    rain/ice pellets must carry the highest severity of all 4 real
    categories - not just an arbitrary value."""
    assert PHASE_SEVERITY["Freezing Rain / Ice Pellets"] == max(PHASE_SEVERITY.values())


# --------------------------------- validate_physics (§11, opt-in PhysicsGuard)


def test_validate_physics_defaults_to_false_and_never_raises_for_out_of_range_input():
    result = compute_real_hydrometeor_phase_at_point(
        temperature_k=500.0, specific_humidity=0.01, pressure_hpa=1000.0
    )
    assert result["is_real_data"] is True


def test_validate_physics_true_passes_silently_for_real_valid_inputs():
    result = compute_real_hydrometeor_phase_at_point(
        temperature_k=290.0, specific_humidity=0.008, pressure_hpa=1000.0, validate_physics=True
    )
    assert result["is_real_data"] is True


def test_validate_physics_true_raises_for_out_of_range_temperature():
    with pytest.raises(RangeError):
        compute_real_hydrometeor_phase_at_point(
            temperature_k=500.0, specific_humidity=0.01, pressure_hpa=1000.0, validate_physics=True
        )


def test_validate_physics_true_raises_for_out_of_range_specific_humidity():
    with pytest.raises(RangeError):
        compute_real_hydrometeor_phase_at_point(
            temperature_k=290.0, specific_humidity=1.5, pressure_hpa=1000.0, validate_physics=True
        )


def test_validate_physics_true_raises_for_out_of_range_pressure():
    with pytest.raises(RangeError):
        compute_real_hydrometeor_phase_at_point(
            temperature_k=290.0, specific_humidity=0.01, pressure_hpa=1.0, validate_physics=True
        )
