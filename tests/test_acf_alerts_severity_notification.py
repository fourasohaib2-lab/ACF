"""Tests for the new acf.alerts additions (severity.py, notification.py),
built while working through the full remaining-gaps list ("On les
attaque toutes un par un") for the ACF-general alerts/ gap:
docs/architecture/acf_awci_architecture_gap_analysis.md's own alerts/
row named these (among others) as missing.

SEVERITY_ORDER is exactly the real Yellow/Orange/Red vocabulary
acf.alerts.warning_engine.OperationalWarning.severity already uses -
not a newly invented scale. WarningNotifier follows the same real
dispatch pattern already established by
awci.alerts.notifications.AlertNotifier.
"""

from __future__ import annotations

import pytest

from acf.alerts.notification import WarningDispatchError, WarningNotifier
from acf.alerts.severity import SEVERITY_ORDER, is_at_least, severity_rank
from acf.alerts.warning_engine import WarningEngine

# --------------------------------------------------------------------- severity.py


def test_severity_order_is_the_real_yellow_orange_red_scale():
    assert SEVERITY_ORDER == ("Yellow", "Orange", "Red")


def test_severity_rank_orders_correctly():
    assert severity_rank("Yellow") == 0
    assert severity_rank("Orange") == 1
    assert severity_rank("Red") == 2


def test_severity_rank_rejects_an_unknown_level():
    with pytest.raises(ValueError, match="Purple"):
        severity_rank("Purple")


def test_is_at_least_compares_real_severity_levels():
    assert is_at_least("Orange", "Yellow") is True
    assert is_at_least("Yellow", "Yellow") is True
    assert is_at_least("Yellow", "Orange") is False
    assert is_at_least("Red", "Orange") is True


# --------------------------------------------------------------------- notification.py


def _real_warning():
    engine = WarningEngine()
    return engine.issue_warning("Thunderstorm", "Orange", 70.0, ["Ile-de-France"])


def test_warning_notifier_calls_every_real_subscriber():
    notifier = WarningNotifier()
    received_a: list[str] = []
    received_b: list[str] = []
    notifier.subscribe(lambda w: received_a.append(w.phenomenon))
    notifier.subscribe(lambda w: received_b.append(w.severity))

    warning = _real_warning()
    errors = notifier.notify((warning,))

    assert received_a == ["Thunderstorm"]
    assert received_b == ["Orange"]
    assert errors == []


def test_warning_notifier_isolates_a_failing_subscriber():
    notifier = WarningNotifier()
    received: list[str] = []
    notifier.subscribe(lambda w: received.append("before"))

    def boom(warning):
        raise ValueError("nope")

    notifier.subscribe(boom)
    notifier.subscribe(lambda w: received.append("after"))

    errors = notifier.notify((_real_warning(),))

    assert received == ["before", "after"]
    assert len(errors) == 1
    assert isinstance(errors[0], WarningDispatchError)
    assert "ValueError" in errors[0].reason


def test_warning_notifier_unsubscribe_stops_future_notifications():
    notifier = WarningNotifier()
    received: list[str] = []

    def callback(w):
        received.append(w.phenomenon)

    notifier.subscribe(callback)
    notifier.unsubscribe(callback)
    notifier.notify((_real_warning(),))
    assert received == []


def test_warning_notifier_with_no_warnings_dispatches_nothing():
    notifier = WarningNotifier()
    calls = []
    notifier.subscribe(lambda w: calls.append(w))
    errors = notifier.notify(())
    assert calls == []
    assert errors == []
