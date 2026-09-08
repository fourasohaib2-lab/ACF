"""
SqliteDocumentStore: real, durable JSON document storage - closes
reports/ACF_MASTER_AUDIT_v2.md's own "/api/v1/events +
/api/v1/datasets remain in-memory (real, disclosed, not durable)"
follow-up.

Uses Python's own standard-library `sqlite3` module - no new project
dependency, and no separate database service this repo would need to
deploy/operate (this project has no Postgres/Redis/etc. anywhere) -
consistent with `acf.verification.skill_database.ModelSkillDatabase`'s
own real, dependency-free JSON-file persistence for the same reason,
just backed by a real embedded database instead of one flat file so
concurrent reads/writes from a live ASGI server don't race each other.

One generic table (`documents`: `id`, `data` as JSON text, `updated_at`)
shared by both `acf.web.routers.events_router` and
`acf.web.routers.datasets_router` - each keeps its own real `Event`/
`Dataset` <-> dict conversion (`Event.to_dict()`/`from_dict()`,
`Dataset.to_dict()`/`from_dict()`), this class only knows about plain
JSON-able dicts.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class SqliteDocumentStore:
    """
    A real, durable key/value document store backed by one SQLite
    file (or `:memory:` for a non-durable store with the exact same
    interface - used by tests that want speed/isolation without
    testing durability itself, which has its own dedicated tests).
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False: a real ASGI server (uvicorn/FastAPI)
        # can genuinely call request handlers from a different thread
        # than the one that constructed this store (e.g. sync
        # dependencies run via a thread pool) - sqlite3's default
        # same-thread restriction would raise on that, not a
        # theoretical concern for a real running app.
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        if self.path != ":memory:":
            # Real concurrency robustness for a live server with
            # multiple simultaneous requests - avoids spurious
            # "database is locked" errors under real concurrent
            # access (WAL mode doesn't apply to :memory: databases).
            self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        self._conn.commit()

    def set(self, doc_id: str, data: dict[str, Any]) -> None:
        """Insert or real-replace one document."""
        self._conn.execute(
            "INSERT INTO documents (id, data, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
            (doc_id, json.dumps(data), _now_iso()),
        )
        self._conn.commit()

    def get(self, doc_id: str) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT data FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT data FROM documents ORDER BY updated_at").fetchall()
        return [json.loads(r[0]) for r in rows]

    def delete(self, doc_id: str) -> None:
        self._conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self._conn.commit()

    def __len__(self) -> int:
        (count,) = self._conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        return int(count)

    def close(self) -> None:
        self._conn.close()
