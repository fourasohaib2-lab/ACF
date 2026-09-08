"""
Tests for acf.events - the Event Engine (docs/reports/ACF_MASTER_AUDIT_v2.md
found this genuinely absent, explicit user request "vas-y, construis
l'Event Engine").
"""

import uuid

import numpy as np
import pytest

from acf.awci.spatial_field import compute_real_complexity_field
from acf.events import Event, IllegalEventTransitionError, detect_fog_favorable_events, detect_strong_wind_events


# --------------------------------------------------------------------- Event


def test_event_defaults_have_a_real_uuid_and_starts_detected():
    event = Event()
    assert uuid.UUID(event.event_id)  # a real, valid UUID4 - not a placeholder string
    assert event.status == "DETECTED"


def test_event_rejects_out_of_range_probability():
    with pytest.raises(ValueError, match="probability"):
        Event(probability=1.5)


def test_event_rejects_out_of_range_confidence():
    with pytest.raises(ValueError, match="confidence"):
        Event(confidence=-0.1)


def test_event_rejects_unknown_initial_status():
    with pytest.raises(ValueError, match="status"):
        Event(status="MADE_UP_STATUS")


# ------------------------------------------------------------------ lifecycle


def test_full_legal_lifecycle_sequence():
    event = Event()
    for step in ("ANALYZED", "CONFIRMED", "VERIFIED", "CERTIFIED", "PUBLISHED"):
        event.transition_to(step)
        assert event.status == step
    assert event.is_terminal() is True


def test_detected_to_rejected_is_legal():
    event = Event()
    event.transition_to("REJECTED")
    assert event.status == "REJECTED"
    assert event.is_terminal() is True


def test_cannot_skip_stages():
    event = Event()
    with pytest.raises(IllegalEventTransitionError):
        event.transition_to("CERTIFIED")  # must go through ANALYZED/CONFIRMED/VERIFIED first


def test_cannot_reject_after_analyzed():
    """Per the master spec's own diagram, REJECTED is only reachable directly from DETECTED."""
    event = Event()
    event.transition_to("ANALYZED")
    with pytest.raises(IllegalEventTransitionError):
        event.transition_to("REJECTED")


def test_cannot_transition_out_of_a_terminal_status():
    event = Event()
    event.transition_to("REJECTED")
    with pytest.raises(IllegalEventTransitionError):
        event.transition_to("ANALYZED")


def test_is_terminal_false_for_intermediate_statuses():
    event = Event()
    event.transition_to("ANALYZED")
    assert event.is_terminal() is False


# ----------------------------------------------------------------- wind_detector


def test_wind_detector_finds_the_real_point_above_threshold():
    wind_field = np.array([[5.0, 25.0], [10.0, 3.0]])  # one real point at 25 m/s
    lats = [10.0, 20.0]
    lons = [0.0, 5.0]

    events = detect_strong_wind_events(wind_field, lats, lons, model="ARPEGE", threshold_m_s=20.0)

    assert len(events) == 1
    assert events[0].type == "strong_wind"
    assert events[0].intensity == 25.0
    assert events[0].geometry == {"lat": 10.0, "lon": 5.0}
    assert events[0].supporting_models == ("ARPEGE",)
    assert events[0].status == "DETECTED"


def test_wind_detector_finds_nothing_below_threshold():
    wind_field = np.array([[5.0, 8.0], [10.0, 3.0]])
    events = detect_strong_wind_events(wind_field, [10.0, 20.0], [0.0, 5.0], model="ARPEGE", threshold_m_s=20.0)
    assert events == []


def test_wind_detector_on_real_solver_output_never_crashes():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)
    events = detect_strong_wind_events(
        result["wind_speed_field"], result["lats"], result["lons"], model="ALADIN", threshold_m_s=0.0
    )
    # threshold 0.0 m/s -> every real point qualifies (wind speed is a non-negative magnitude).
    assert len(events) == 6 * 10
    assert all(e.intensity >= 0.0 for e in events)


# ------------------------------------------------------------------ fog_detector


def test_fog_detector_matches_the_real_metpy_reference_value():
    """
    Regression-locks the exact real MetPy relative_humidity_from_specific_humidity()
    value for known inputs (verified once by hand: T=20degC, P=1000hPa,
    q=0.01 kg/kg -> RH=68.449...%), so a future accidental change to
    this detector's real physics call is caught.
    """
    temperature = np.array([[293.15]])  # 20 degC
    specific_humidity = np.array([[0.01]])
    pressure = np.array([[1000.0]])
    wind = np.array([[0.0]])  # calm - satisfies the wind precondition regardless

    events = detect_fog_favorable_events(
        temperature, specific_humidity, pressure, wind, [10.0], [0.0], model="ARPEGE", rh_threshold_pct=0.0
    )

    assert len(events) == 1
    assert events[0].intensity == pytest.approx(68.449, abs=0.01)


def test_fog_detector_requires_both_high_humidity_and_calm_wind():
    temperature = np.array([[293.15, 293.15]])
    specific_humidity = np.array([[0.014, 0.014]])  # both near-saturated
    pressure = np.array([[1000.0, 1000.0]])
    wind = np.array([[0.5, 10.0]])  # first calm, second windy

    events = detect_fog_favorable_events(
        temperature, specific_humidity, pressure, wind, [10.0], [0.0, 5.0], model="ARPEGE", rh_threshold_pct=95.0
    )

    assert len(events) == 1
    assert events[0].geometry == {"lat": 10.0, "lon": 0.0}  # only the calm point


def test_fog_detector_event_type_is_not_confirmed_fog():
    """Honest naming check - never claims confirmed fog, only its precondition."""
    temperature = np.array([[293.15]])
    specific_humidity = np.array([[0.014]])
    pressure = np.array([[1000.0]])
    wind = np.array([[0.0]])

    events = detect_fog_favorable_events(
        temperature, specific_humidity, pressure, wind, [10.0], [0.0], model="ARPEGE", rh_threshold_pct=50.0
    )
    assert events[0].type == "fog_favorable_conditions"
    assert events[0].type != "fog"


def test_fog_detector_intensity_clamped_but_raw_value_preserved():
    """A supersaturated RH result (real MetPy formula can exceed 100% for extreme inputs) must clamp the headline intensity but keep the real raw value visible."""
    temperature = np.array([[285.0]])
    specific_humidity = np.array([[0.014]])  # combination known to push RH above 100% at this pressure/temp
    pressure = np.array([[950.0]])
    wind = np.array([[0.0]])

    events = detect_fog_favorable_events(
        temperature, specific_humidity, pressure, wind, [10.0], [0.0], model="ARPEGE", rh_threshold_pct=0.0
    )
    assert events[0].intensity <= 100.0
    assert events[0].supporting_parameters["relative_humidity_pct_raw"] >= events[0].intensity


def test_fog_detector_on_real_solver_output_never_crashes():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)
    events = detect_fog_favorable_events(
        result["temperature_field"],
        result["specific_humidity_field"],
        result["pressure_field_hpa"],
        result["wind_speed_field"],
        result["lats"],
        result["lons"],
        model="ALADIN",
    )
    # No assertion on count - real conditions may or may not qualify; this only
    # proves the real MetPy call works end-to-end on real solver output.
    for event in events:
        assert event.type == "fog_favorable_conditions"
        assert 0.0 <= event.intensity <= 100.0
