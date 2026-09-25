"""Real state-transition tests for AlertHistoryLog (Master Prompt §23
"historical alerts... acknowledgement/read state") - see
acf.gui.dashboard.awci_alert_history's own module docstring for the
exact real rules being tested here."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from acf.gui.dashboard.awci_alert_history import AlertHistoryLog

_T0 = datetime(2026, 9, 20, 12, 0, 0, tzinfo=timezone.utc)


def test_a_new_elevated_row_creates_exactly_one_new_entry():
    log = AlertHistoryLog()
    rows = [("🌪️", "Turbulence", "High", 72.0)]
    new_entries = log.record(rows, area="Global", valid_time="12:00 UTC", now=_T0)
    assert len(new_entries) == 1
    assert new_entries[0].label == "Turbulence"
    assert new_entries[0].first_seen == _T0
    assert new_entries[0].is_active


def test_the_same_elevated_row_across_refreshes_does_not_duplicate():
    log = AlertHistoryLog()
    rows = [("🌪️", "Turbulence", "High", 72.0)]
    log.record(rows, area="Global", valid_time="12:00 UTC", now=_T0)
    t1 = _T0 + timedelta(minutes=5)
    rows_2 = [("🌪️", "Turbulence", "Very High", 80.0)]
    new_entries = log.record(rows_2, area="Global", valid_time="12:05 UTC", now=t1)

    assert new_entries == []
    assert len(log.all_entries()) == 1
    entry = log.active_entries()[0]
    assert entry.level == "Very High"
    assert entry.score == 80.0
    assert entry.last_seen == t1
    assert entry.first_seen == _T0


def test_a_hazard_dropping_below_threshold_resolves_its_entry():
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    t1 = _T0 + timedelta(minutes=10)
    log.record([], area="Global", valid_time="12:10 UTC", now=t1)

    assert log.active_entries() == []
    history = log.all_entries()
    assert len(history) == 1
    assert history[0].resolved_at == t1
    assert not history[0].is_active


def test_a_resolved_hazard_re_elevating_creates_a_second_distinct_entry():
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    t1 = _T0 + timedelta(minutes=10)
    log.record([], area="Global", valid_time="12:10 UTC", now=t1)
    t2 = _T0 + timedelta(minutes=20)
    new_entries = log.record([("🌪️", "Turbulence", "Extreme", 90.0)], area="Global", valid_time="12:20 UTC", now=t2)

    assert len(new_entries) == 1
    assert len(log.all_entries()) == 2
    assert len(log.active_entries()) == 1
    assert log.active_entries()[0].first_seen == t2


def test_acknowledge_sets_real_state_and_returns_true():
    log = AlertHistoryLog()
    [entry] = log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    ack_time = _T0 + timedelta(minutes=1)

    assert entry.acknowledged is False
    result = log.acknowledge(entry.entry_id, now=ack_time)

    assert result is True
    assert entry.acknowledged is True
    assert entry.acknowledged_at == ack_time


def test_acknowledge_an_unknown_entry_id_returns_false():
    log = AlertHistoryLog()
    assert log.acknowledge("does-not-exist") is False


def test_unacknowledged_active_count_only_counts_active_unacknowledged():
    log = AlertHistoryLog()
    rows = [
        ("🌪️", "Turbulence", "High", 72.0),
        ("⛈️", "Convection", "Extreme", 91.0),
    ]
    entries = log.record(rows, area="Global", valid_time="12:00 UTC", now=_T0)
    assert log.unacknowledged_active_count() == 2

    log.acknowledge(entries[0].entry_id, now=_T0)
    assert log.unacknowledged_active_count() == 1


def test_two_distinct_hazards_in_the_same_refresh_both_get_their_own_entry():
    log = AlertHistoryLog()
    rows = [
        ("🌪️", "Turbulence", "High", 72.0),
        ("⛈️", "Convection", "Extreme", 91.0),
    ]
    new_entries = log.record(rows, area="Global", valid_time="12:00 UTC", now=_T0)
    assert {e.label for e in new_entries} == {"Turbulence", "Convection"}
    assert len(log.active_entries()) == 2


def test_all_entries_sorted_newest_first_seen_first():
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    t1 = _T0 + timedelta(minutes=10)
    log.record([], area="Global", valid_time="12:10 UTC", now=t1)
    t2 = _T0 + timedelta(minutes=20)
    log.record([("⛈️", "Convection", "Extreme", 91.0)], area="Global", valid_time="12:20 UTC", now=t2)

    labels = [e.label for e in log.all_entries()]
    assert labels == ["Convection", "Turbulence"]
