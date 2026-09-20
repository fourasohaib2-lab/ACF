"""
AWCI Alert History Log
========================

Real, timestamped alert history + acknowledgement state - closes the
gap this dashboard's own docstrings already disclosed honestly
(`awci_footer_summary.py`: "this dashboard has no real per-alert event
log to draw individual past timestamps from"; the AWCI Master Prompt's
own §23 asks for "active alerts, historical alerts, severity,
timestamp, affected area, affected altitude, acknowledgement/read
state").

Real state transitions, never a fabricated log
------------------------------------------------
`AlertHistoryLog.record()` is called on every real dashboard refresh
with the SAME real elevated-risk rows `compute_elevated_risks()`
already produces (never a second/independent hazard computation). A
new `AlertLogEntry` is created only the first real time a given hazard
label transitions from "not elevated" to "elevated" - not once per
refresh (that would spam the log with the same real condition every
few seconds). While a hazard stays elevated across refreshes, its
existing entry's `last_seen`/`level`/`score` are updated in place, not
duplicated. When a hazard drops back below the elevated threshold, its
entry is marked `resolved_at` (a real wall-clock timestamp) and moves
from "active" to "history only" - it is never deleted, so the log stays
a real, honest record of what happened and when.

`acknowledge()` sets a real `acknowledged`/`acknowledged_at` on a
specific entry, driven only by a real user click
(`AWCIAlertsDialog`'s own "Acknowledge" button) - never auto-set.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AlertLogEntry:
    """One real, timestamped alert lifecycle record."""

    entry_id: str
    icon: str
    label: str
    level: str
    score: float
    area: str
    valid_time: str
    first_seen: datetime
    last_seen: datetime
    acknowledged: bool = False
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.resolved_at is None


class AlertHistoryLog:
    """Real in-session alert history + acknowledgement tracker - see
    module docstring for the real state-transition rules."""

    def __init__(self) -> None:
        #: label -> currently-active entry (not yet resolved).
        self._active: dict[str, AlertLogEntry] = {}
        #: every entry ever created, newest first once sorted by a
        #: caller - insertion order here, active and resolved alike.
        self._history: list[AlertLogEntry] = []

    def record(
        self,
        elevated_rows: list[tuple[str, str, str, float]],
        area: str,
        valid_time: str,
        now: datetime | None = None,
    ) -> list[AlertLogEntry]:
        """Real state-transition update from the current real elevated
        rows (`compute_elevated_risks()`'s own return value). Returns
        the entries genuinely newly created by this call (empty list
        when every currently-elevated hazard was already logged)."""
        now = now or datetime.now(timezone.utc)
        current_labels = {label for _icon, label, _level, _score in elevated_rows}
        new_entries: list[AlertLogEntry] = []

        for icon, label, level, score in elevated_rows:
            existing = self._active.get(label)
            if existing is not None:
                existing.last_seen = now
                existing.level = level
                existing.score = score
                existing.area = area
                existing.valid_time = valid_time
                continue
            entry = AlertLogEntry(
                entry_id=f"{label}@{now.isoformat()}",
                icon=icon,
                label=label,
                level=level,
                score=score,
                area=area,
                valid_time=valid_time,
                first_seen=now,
                last_seen=now,
            )
            self._active[label] = entry
            self._history.append(entry)
            new_entries.append(entry)

        for label in list(self._active):
            if label not in current_labels:
                self._active.pop(label).resolved_at = now

        return new_entries

    def acknowledge(self, entry_id: str, now: datetime | None = None) -> bool:
        """Real user acknowledgement of one specific entry (active or
        already resolved). Returns False if `entry_id` is not real
        (unknown) - never silently no-ops without telling the caller."""
        for entry in self._history:
            if entry.entry_id == entry_id:
                entry.acknowledged = True
                entry.acknowledged_at = now or datetime.now(timezone.utc)
                return True
        return False

    def active_entries(self) -> list[AlertLogEntry]:
        """Currently-elevated entries, worst real score first."""
        return sorted(self._active.values(), key=lambda e: e.score, reverse=True)

    def all_entries(self) -> list[AlertLogEntry]:
        """Every real entry ever logged this session, most recent
        first_seen first."""
        return sorted(self._history, key=lambda e: e.first_seen, reverse=True)

    def unacknowledged_active_count(self) -> int:
        return sum(1 for entry in self._active.values() if not entry.acknowledged)
