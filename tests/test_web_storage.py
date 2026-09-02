"""
Tests for acf.web.storage.SqliteDocumentStore - the real durable
storage backing /api/v1/events and /api/v1/datasets (closes
reports/ACF_MASTER_AUDIT_v2.md's own "remain in-memory (real,
disclosed, not durable)" follow-up).
"""

from __future__ import annotations

from acf.web.storage import SqliteDocumentStore


def test_set_and_get_round_trip():
    store = SqliteDocumentStore(":memory:")
    store.set("a", {"x": 1, "y": [1, 2, 3]})
    assert store.get("a") == {"x": 1, "y": [1, 2, 3]}


def test_get_returns_none_for_an_unknown_id():
    store = SqliteDocumentStore(":memory:")
    assert store.get("does-not-exist") is None


def test_set_overwrites_an_existing_document():
    store = SqliteDocumentStore(":memory:")
    store.set("a", {"v": 1})
    store.set("a", {"v": 2})
    assert store.get("a") == {"v": 2}
    assert len(store) == 1


def test_list_returns_every_document():
    store = SqliteDocumentStore(":memory:")
    store.set("a", {"v": 1})
    store.set("b", {"v": 2})
    docs = store.list()
    assert {d["v"] for d in docs} == {1, 2}


def test_delete_removes_a_document():
    store = SqliteDocumentStore(":memory:")
    store.set("a", {"v": 1})
    store.delete("a")
    assert store.get("a") is None
    assert len(store) == 0


def test_len_reflects_the_real_row_count():
    store = SqliteDocumentStore(":memory:")
    assert len(store) == 0
    store.set("a", {})
    store.set("b", {})
    assert len(store) == 2


# ------------------------------------------------------------------ real durability across a restart


def test_data_survives_closing_and_reopening_the_same_real_file(tmp_path):
    """The actual property that distinguishes this from the old in-memory dict: real data on disk, still there after the process-level object is gone and a fresh one opens the same file."""
    path = tmp_path / "store.db"

    store1 = SqliteDocumentStore(path)
    store1.set("a", {"real": "data", "n": 42})
    store1.close()

    store2 = SqliteDocumentStore(path)
    assert store2.get("a") == {"real": "data", "n": 42}
    assert len(store2) == 1


def test_memory_store_does_not_survive_a_reopen():
    """Sanity check on the distinction itself: ":memory:" is real SQLite, but genuinely not durable - a fresh connection to it is a fresh, empty database, not the same one."""
    path = ":memory:"
    store1 = SqliteDocumentStore(path)
    store1.set("a", {"v": 1})

    store2 = SqliteDocumentStore(path)
    assert store2.get("a") is None


def test_creates_parent_directories_for_a_real_file_path(tmp_path):
    path = tmp_path / "nested" / "dir" / "store.db"
    store = SqliteDocumentStore(path)
    store.set("a", {"v": 1})
    assert path.exists()
