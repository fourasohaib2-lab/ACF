"""
Tests for AWCIDashboard's real alert-history persistence wiring
(Master Prompt §23, added 2026-09-20) - alert_history_path constructor
parameter, _persist_alert_history_if_dirty(), and the real load-on-
construct behavior. See awci_alert_history.py's own module docstring
for the underlying AlertHistoryLog.save()/load() design.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_default_construction_never_touches_disk(qapp, tmp_path, monkeypatch):
    """The default (alert_history_path=None) must stay exactly as
    in-memory-only as before this parameter existed - real regression
    guard against every existing GUI test in this suite silently
    starting to read/write a real file."""
    import acf.gui.dashboard.awci_alert_history as alert_history_module

    fake_default = tmp_path / "should_never_be_created.json"
    monkeypatch.setattr(alert_history_module, "DEFAULT_ALERT_HISTORY_PATH", fake_default)

    dashboard = AWCIDashboard()

    assert dashboard._alert_history_path is None
    assert not fake_default.exists()


def test_construction_with_a_path_persists_a_real_file(qapp, tmp_path):
    path = tmp_path / "history.json"
    dashboard = AWCIDashboard(alert_history_path=path)

    # The default demo point of interest has a real elevated Turbulence
    # hazard (same value every other panel on this dashboard already
    # shows) - a real refresh at construction time must have recorded
    # and persisted it.
    assert path.exists()
    assert len(dashboard.alert_history.all_entries()) >= 1


def test_a_second_dashboard_with_the_same_path_reloads_the_real_history(qapp, tmp_path):
    path = tmp_path / "history.json"
    first = AWCIDashboard(alert_history_path=path)
    first_count = len(first.alert_history.all_entries())
    assert first_count >= 1

    second = AWCIDashboard(alert_history_path=path)

    assert len(second.alert_history.all_entries()) == first_count


def test_acknowledging_an_alert_persists_immediately(qapp, tmp_path):
    path = tmp_path / "history.json"
    dashboard = AWCIDashboard(alert_history_path=path)
    entry = dashboard.alert_history.all_entries()[0]
    assert entry.acknowledged is False

    dashboard._on_alert_acknowledged(entry.entry_id)

    from acf.gui.dashboard.awci_alert_history import AlertHistoryLog

    reloaded = AlertHistoryLog()
    reloaded.load(path)
    assert reloaded.all_entries()[0].acknowledged is True


def test_persist_helper_is_a_real_no_op_without_a_configured_path(qapp, tmp_path):
    dashboard = AWCIDashboard()
    dashboard.alert_history.is_dirty = True

    dashboard._persist_alert_history_if_dirty()  # must not raise, must not write anywhere

    assert dashboard.alert_history.is_dirty is True  # never cleared - nothing was actually saved
