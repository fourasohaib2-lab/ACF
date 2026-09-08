"""
Tests for acf.gui.esoc.panel_manager.MPIDomainTopologyPanel - the real
MPI domain-decomposition panel closing the previously-dead "HPC / MPI
Domain Topology" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import MPIDomainTopologyPanel
from acf.hpc.simulation.mpi_domain import MPIDomainDecomposition


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_starts_with_one_real_row_per_rank(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = MPIDomainTopologyPanel(registry, dispatcher)

    assert panel.table.rowCount() == panel.n_proc_lat.value() * panel.n_proc_lon.value()


def test_bounds_match_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = MPIDomainTopologyPanel(registry, dispatcher)
    panel.global_nlat.setValue(36)
    panel.global_nlon.setValue(72)
    panel.n_proc_lat.setValue(2)
    panel.n_proc_lon.setValue(4)

    panel.button.click()

    for rank in range(8):
        expected = MPIDomainDecomposition(36, 72, 2, 4, rank).get_local_bounds()
        row = [int(panel.table.item(rank, col).text()) for col in range(1, 5)]
        assert tuple(row) == expected


def test_every_real_rank_tiles_the_global_grid_without_gaps_or_overlap(qapp, registry):
    """Real sanity check: the union of every rank's own real bounds
    must exactly reconstruct the full global grid - no real point
    double-counted or missed."""
    dispatcher = CommandDispatcher()
    panel = MPIDomainTopologyPanel(registry, dispatcher)
    panel.global_nlat.setValue(36)
    panel.global_nlon.setValue(72)
    panel.n_proc_lat.setValue(2)
    panel.n_proc_lon.setValue(4)
    panel.button.click()

    import numpy as np

    coverage = np.zeros((36, 72), dtype=int)
    for rank in range(8):
        lat_start, lat_end, lon_start, lon_end = (
            int(panel.table.item(rank, col).text()) for col in range(1, 5)
        )
        coverage[lat_start:lat_end, lon_start:lon_end] += 1

    assert np.all(coverage == 1)


def test_changing_the_process_grid_updates_the_real_row_count(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = MPIDomainTopologyPanel(registry, dispatcher)

    panel.n_proc_lat.setValue(3)
    panel.n_proc_lon.setValue(3)
    panel.button.click()

    assert panel.table.rowCount() == 9


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["mpi_domain"] = None

    panel = MPIDomainTopologyPanel(registry, dispatcher)

    assert not hasattr(panel, "button")
