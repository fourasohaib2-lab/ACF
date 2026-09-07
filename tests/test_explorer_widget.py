"""
Tests for acf.gui.widgets.ExplorerWidget - previously had zero test
coverage (found while smoke-testing ClassicDashboardWindow's File/Data
menu actions end to end, a code path its own module docstring says was
"designed" piece by piece but "never assembled behind one real window
until now").

NOTE (correction, 2026-09-07): refresh_datasets() used to
unconditionally addTopLevelItem() a new "Datasets" branch on every
call, with nothing removing a prior one - confirmed by direct test
(topLevelItemCount() grew 1, 2, 3, 4... across 4 calls with no dataset
ever actually removed). MenuManager.refresh_dataset_view() is the only
real caller, and it runs every time a dataset is opened - an ordinary
session opening more than one dataset left duplicate "Datasets"
branches stacked in the tree. Fixed by removing any existing "Datasets"
branch before adding the new one.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from acf.gui.widgets.explorer import ExplorerWidget


class _FakeDataset:
    def __init__(self, name: str, variables: list[str] | None = None) -> None:
        self.name = name
        self.variable_names = variables or ["t2m"]


class _FakeProject:
    def __init__(self, name: str, root_path: str) -> None:
        self.name = name
        self.root_path = root_path


def test_refresh_datasets_does_not_accumulate_duplicate_branches(qtbot):
    explorer = ExplorerWidget()
    qtbot.addWidget(explorer)

    for i in range(4):
        explorer.refresh_datasets([_FakeDataset(f"dataset_{i}")])

    dataset_branches = [
        explorer.topLevelItem(i) for i in range(explorer.topLevelItemCount()) if explorer.topLevelItem(i).text(0) == "🌦 Datasets"
    ]
    assert len(dataset_branches) == 1
    assert explorer.topLevelItemCount() == 1


def test_refresh_datasets_replacement_reflects_the_latest_call(qtbot):
    explorer = ExplorerWidget()
    qtbot.addWidget(explorer)

    explorer.refresh_datasets([_FakeDataset("old_dataset")])
    explorer.refresh_datasets([_FakeDataset("new_dataset")])

    dataset_root = explorer.topLevelItem(0)
    child_names = [dataset_root.child(i).text(0) for i in range(dataset_root.childCount())]
    assert "new_dataset" in child_names
    assert "old_dataset" not in child_names


def test_refresh_datasets_preserves_an_already_loaded_project_branch(qtbot):
    explorer = ExplorerWidget()
    qtbot.addWidget(explorer)

    project_dir = tempfile.mkdtemp()
    explorer.load_project(_FakeProject("MyProject", project_dir))

    explorer.refresh_datasets([_FakeDataset("ds_1")])
    explorer.refresh_datasets([_FakeDataset("ds_2")])

    labels = [explorer.topLevelItem(i).text(0) for i in range(explorer.topLevelItemCount())]
    assert labels.count("🌦 Datasets") == 1
    assert "MyProject" in labels


def test_load_project_replaces_the_previous_project_tree(qtbot):
    explorer = ExplorerWidget()
    qtbot.addWidget(explorer)

    explorer.load_project(_FakeProject("FirstProject", tempfile.mkdtemp()))
    explorer.load_project(_FakeProject("SecondProject", tempfile.mkdtemp()))

    labels = [explorer.topLevelItem(i).text(0) for i in range(explorer.topLevelItemCount())]
    assert labels == ["SecondProject"]


def test_load_project_with_none_clears_the_tree(qtbot):
    explorer = ExplorerWidget()
    qtbot.addWidget(explorer)

    explorer.load_project(_FakeProject("SomeProject", tempfile.mkdtemp()))
    explorer.load_project(None)

    assert explorer.topLevelItemCount() == 0
