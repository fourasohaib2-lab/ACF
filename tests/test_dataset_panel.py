"""
Tests for acf.gui.docks.dataset_panel.DatasetPanel - had zero test
coverage before this file (found while auditing the same
ClassicDashboardWindow assembly that produced the ExplorerWidget
duplicate-branch bug: real pieces, tested in isolation elsewhere,
wired together for the first time, never exercised end-to-end).

NOTE (correction, 2026-09-07): refresh() used to display every real
dataset as "Unnamed Dataset" with zero variable children.
acf.catalog.dataset_registry.DatasetRegistry.datasets is a @property
returning a dict (id -> dataset object) - never callable() - so
refresh()'s `for dataset in datasets:` iterated the dict's KEYS (plain
id strings, which have no .name/.variables) rather than its values.
Confirmed by a direct test registering 2 real datasets and checking
what the tree actually displayed. Fixed by converting a dict result to
its .values() before iterating.
"""

from __future__ import annotations

from acf.data.manager import DataManager
from acf.gui.docks.dataset_panel import DatasetPanel


class _FakeDataset:
    def __init__(self, name: str, variables: list[str]) -> None:
        self.name = name
        self.variables = variables
        self.id = name


def test_refresh_shows_the_real_dataset_name_not_unnamed_dataset(qtbot):
    dm = DataManager()
    dm.registry.register(_FakeDataset("ERA5_2026090700", ["t2m", "u10"]))

    panel = DatasetPanel()
    qtbot.addWidget(panel)
    panel.set_data_manager(dm)

    assert panel.dataset_count() == 1
    item = panel.tree.topLevelItem(0)
    assert item.text(0) == "ERA5_2026090700"
    assert item.text(0) != "Unnamed Dataset"


def test_refresh_shows_the_real_dataset_variables_as_children(qtbot):
    dm = DataManager()
    dm.registry.register(_FakeDataset("ARPEGE_20260907", ["msl", "z500", "t850"]))

    panel = DatasetPanel()
    qtbot.addWidget(panel)
    panel.set_data_manager(dm)

    item = panel.tree.topLevelItem(0)
    assert item.childCount() == 3
    child_labels = {item.child(i).text(0) for i in range(item.childCount())}
    assert child_labels == {"msl", "z500", "t850"}


def test_refresh_handles_multiple_real_datasets_independently(qtbot):
    dm = DataManager()
    dm.registry.register(_FakeDataset("DatasetA", ["u", "v"]))
    dm.registry.register(_FakeDataset("DatasetB", ["w"]))

    panel = DatasetPanel()
    qtbot.addWidget(panel)
    panel.set_data_manager(dm)

    assert panel.dataset_count() == 2
    labels = {panel.tree.topLevelItem(i).text(0) for i in range(2)}
    assert labels == {"DatasetA", "DatasetB"}


def test_refresh_with_no_data_manager_is_empty_and_does_not_raise(qtbot):
    panel = DatasetPanel()
    qtbot.addWidget(panel)

    panel.refresh()

    assert panel.dataset_count() == 0


def test_refresh_with_empty_registry_is_empty(qtbot):
    dm = DataManager()

    panel = DatasetPanel()
    qtbot.addWidget(panel)
    panel.set_data_manager(dm)

    assert panel.dataset_count() == 0


def test_selected_item_returns_the_real_dataset_object(qtbot):
    dm = DataManager()
    dataset = _FakeDataset("SelectedDataset", [])
    dm.registry.register(dataset)

    panel = DatasetPanel()
    qtbot.addWidget(panel)
    panel.set_data_manager(dm)

    item = panel.tree.topLevelItem(0)
    item.setSelected(True)

    assert panel.selected_item() is dataset


def test_clear_empties_the_tree(qtbot):
    dm = DataManager()
    dm.registry.register(_FakeDataset("SomeDataset", []))

    panel = DatasetPanel()
    qtbot.addWidget(panel)
    panel.set_data_manager(dm)
    assert panel.dataset_count() == 1

    panel.clear()

    assert panel.dataset_count() == 0
