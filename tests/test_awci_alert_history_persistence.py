"""Real save/load tests for AlertHistoryLog (Master Prompt §23's own
"historical alerts" persisted across restarts - added 2026-09-20,
closing the "in-session only" limitation the first version of this
module disclosed). See awci_alert_history.py's own module docstring
for the real ~/.acf/ convention this follows
(acf.workspace.recent.RecentProjectsManager)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from acf.gui.dashboard.awci_alert_history import AlertHistoryLog

_T0 = datetime(2026, 9, 20, 12, 0, 0, tzinfo=timezone.utc)


def test_record_marks_is_dirty_true(tmp_path):
    log = AlertHistoryLog()
    assert log.is_dirty is False
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    assert log.is_dirty is True


def test_save_clears_is_dirty_and_writes_a_real_file(tmp_path):
    path = tmp_path / "history.json"
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)

    log.save(path)

    assert log.is_dirty is False
    assert path.exists()
    data = json.loads(path.read_text())
    assert len(data["entries"]) == 1
    assert data["entries"][0]["label"] == "Turbulence"


def test_load_restores_entries_with_correct_types(tmp_path):
    path = tmp_path / "history.json"
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    log.acknowledge(log.all_entries()[0].entry_id, now=_T0 + timedelta(minutes=1))
    log.save(path)

    loaded = AlertHistoryLog()
    loaded.load(path)

    [entry] = loaded.all_entries()
    assert entry.label == "Turbulence"
    assert entry.level == "High"
    assert entry.score == 72.0
    assert entry.first_seen == _T0
    assert entry.acknowledged is True
    assert entry.acknowledged_at == _T0 + timedelta(minutes=1)
    assert entry.resolved_at is None
    assert loaded.is_dirty is False


def test_load_reconstructs_active_entries_for_still_unresolved_hazards(tmp_path):
    path = tmp_path / "history.json"
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    log.save(path)

    loaded = AlertHistoryLog()
    loaded.load(path)

    assert len(loaded.active_entries()) == 1
    assert loaded.active_entries()[0].label == "Turbulence"


def test_load_does_not_reconstruct_active_entries_for_resolved_hazards(tmp_path):
    path = tmp_path / "history.json"
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    log.record([], area="Global", valid_time="12:10 UTC", now=_T0 + timedelta(minutes=10))
    log.save(path)

    loaded = AlertHistoryLog()
    loaded.load(path)

    assert loaded.active_entries() == []
    assert len(loaded.all_entries()) == 1


def test_a_reloaded_active_entry_resolves_normally_on_the_next_real_record(tmp_path):
    """A hazard that was still active when the app closed must behave
    exactly like a freshly-created active entry once real refreshes
    resume - resolving it if it's no longer elevated."""
    path = tmp_path / "history.json"
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)
    log.save(path)

    loaded = AlertHistoryLog()
    loaded.load(path)
    t1 = _T0 + timedelta(hours=1)
    loaded.record([], area="Global", valid_time="13:00 UTC", now=t1)

    assert loaded.active_entries() == []
    assert loaded.all_entries()[0].resolved_at == t1


def test_load_of_a_missing_file_is_an_honest_empty_log_not_an_error(tmp_path):
    path = tmp_path / "does_not_exist.json"
    log = AlertHistoryLog()
    log.load(path)
    assert log.all_entries() == []
    assert log.is_dirty is False


def test_load_of_a_corrupted_file_logs_a_warning_and_starts_empty(tmp_path, caplog):
    path = tmp_path / "corrupted.json"
    path.write_text("{ not valid json ")

    log = AlertHistoryLog()
    with caplog.at_level("WARNING"):
        log.load(path)

    assert log.all_entries() == []
    assert any("Failed to load alert history" in record.message for record in caplog.records)


def test_save_creates_the_parent_directory_if_missing(tmp_path):
    path = tmp_path / "nested" / "dir" / "history.json"
    log = AlertHistoryLog()
    log.record([("🌪️", "Turbulence", "High", 72.0)], area="Global", valid_time="12:00 UTC", now=_T0)

    log.save(path)

    assert path.exists()


def test_round_trip_preserves_multiple_entries_active_and_resolved(tmp_path):
    path = tmp_path / "history.json"
    log = AlertHistoryLog()
    log.record(
        [("🌪️", "Turbulence", "High", 72.0), ("⛈️", "Convection", "Extreme", 91.0)],
        area="Global", valid_time="12:00 UTC", now=_T0,
    )
    t1 = _T0 + timedelta(minutes=10)
    log.record([("⛈️", "Convection", "Extreme", 91.0)], area="Global", valid_time="12:10 UTC", now=t1)
    log.save(path)

    loaded = AlertHistoryLog()
    loaded.load(path)

    labels_active = {e.label for e in loaded.active_entries()}
    labels_all = {e.label for e in loaded.all_entries()}
    assert labels_active == {"Convection"}
    assert labels_all == {"Turbulence", "Convection"}
