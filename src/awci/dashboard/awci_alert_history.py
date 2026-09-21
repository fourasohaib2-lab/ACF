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

Real persistence across app restarts (added 2026-09-20, closes the
disclosed "in-session only" limitation of this module's first version)
--------------------------------------------------------------------
`save()`/`load()` follow the SAME real convention already established
by `acf.workspace.recent.RecentProjectsManager` for local app state -
a real JSON file under `~/.acf/` (here: `awci_alert_history.json`),
not a new/second persistence mechanism. `load()` never silently
discards a genuinely corrupted file (same bug class already found and
fixed twice elsewhere in this codebase, per `RecentProjectsManager.
load()`'s own docstring) - it logs a real warning and starts from an
empty log instead. `save()` is called by the caller (`AWCIDashboard`)
only when `is_dirty` is true (a real mutation happened - a new entry,
a resolution, or an acknowledgement), not on every refresh, to avoid
real, unnecessary disk I/O on the GUI thread for the common case where
nothing changed.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("acf.gui.dashboard.awci_alert_history")

#: Same real ~/.acf/ convention as acf.workspace.recent.RecentProjectsManager.
DEFAULT_ALERT_HISTORY_PATH = Path.home() / ".acf" / "awci_alert_history.json"


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

    def to_dict(self) -> dict[str, Any]:
        """Real JSON-serializable form - see module docstring's own
        persistence section."""
        return {
            "entry_id": self.entry_id,
            "icon": self.icon,
            "label": self.label,
            "level": self.level,
            "score": self.score,
            "area": self.area,
            "valid_time": self.valid_time,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertLogEntry:
        return cls(
            entry_id=data["entry_id"],
            icon=data["icon"],
            label=data["label"],
            level=data["level"],
            score=data["score"],
            area=data["area"],
            valid_time=data["valid_time"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            acknowledged=data.get("acknowledged", False),
            acknowledged_at=datetime.fromisoformat(data["acknowledged_at"]) if data.get("acknowledged_at") else None,
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None,
        )


class AlertHistoryLog:
    """Real in-session alert history + acknowledgement tracker - see
    module docstring for the real state-transition rules."""

    def __init__(self) -> None:
        #: label -> currently-active entry (not yet resolved).
        self._active: dict[str, AlertLogEntry] = {}
        #: every entry ever created, newest first once sorted by a
        #: caller - insertion order here, active and resolved alike.
        self._history: list[AlertLogEntry] = []
        #: True after a real mutation (new entry/resolve/acknowledge)
        #: not yet written by save() - see module docstring's own
        #: persistence section for why the caller checks this instead
        #: of saving unconditionally on every call.
        self.is_dirty: bool = False

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
            self.is_dirty = True

        for label in list(self._active):
            if label not in current_labels:
                self._active.pop(label).resolved_at = now
                self.is_dirty = True

        return new_entries

    def acknowledge(self, entry_id: str, now: datetime | None = None) -> bool:
        """Real user acknowledgement of one specific entry (active or
        already resolved). Returns False if `entry_id` is not real
        (unknown) - never silently no-ops without telling the caller."""
        for entry in self._history:
            if entry.entry_id == entry_id:
                entry.acknowledged = True
                entry.acknowledged_at = now or datetime.now(timezone.utc)
                self.is_dirty = True
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

    def save(self, path: Path | None = None) -> None:
        """Real, synchronous write to a real JSON file - see module
        docstring's own persistence section. Raises OSError on a real
        write failure (disk full, permission denied) - the caller
        decides how to surface that (same convention as
        AWCIDashboard._save_scenario()'s own explicit try/except)."""
        path = path or DEFAULT_ALERT_HISTORY_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"entries": [entry.to_dict() for entry in self._history]}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        self.is_dirty = False

    def load(self, path: Path | None = None) -> None:
        """Real load from a real JSON file - a missing file is an
        honest "nothing logged yet" (empty log, not an error). A
        genuinely corrupted file logs a real warning and starts from
        an empty log instead of silently discarding it without a
        trace - same real bug class already found and fixed twice
        elsewhere in this codebase (see
        acf.workspace.recent.RecentProjectsManager.load()'s own
        docstring)."""
        path = path or DEFAULT_ALERT_HISTORY_PATH
        self._active = {}
        self._history = []
        self.is_dirty = False
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            entries = [AlertLogEntry.from_dict(raw) for raw in data.get("entries", [])]
        except Exception:
            logger.warning(
                "Failed to load alert history from %s - starting from an empty log instead",
                path,
                exc_info=True,
            )
            return
        self._history = entries
        self._active = {entry.label: entry for entry in entries if entry.is_active}
