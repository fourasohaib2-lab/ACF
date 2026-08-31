"""Unit test suite for ACF SURFEX Operational Subsystem (ACF-HPC-105)."""

from acf.surfex.engine import SurfexEngine
from acf.surfex.land_surface import ISBA, TEB
from acf.surfex.snow import CROCUS, SnowDiagnostics
from acf.surfex.urban import TownEnergyBalance


def test_surfex_engine_simulation():
    surfex = SurfexEngine()
    res = surfex.run_simulation(forcing_file="arome_forcing.nc", domain="Algerie_Nord")
    # CORRECTED: "status" used to be unconditionally "SUCCESS" regardless
    # of whether the underlying job actually reached a real SLURM
    # scheduler - it now honestly propagates JobManager's
    # "is_real_submission" signal, and no real scheduler is connected
    # in this test environment.
    assert res["status"] != "SUCCESS"
    assert res["is_real_submission"] is False
    assert res["domain"] == "Algerie_Nord"
    assert "job_id" in res


def test_surfex_schemes():
    assert ISBA.run() is True
    assert TEB.run() is True
    assert CROCUS.run() is True
    assert TownEnergyBalance.solve() is True
    diag = SnowDiagnostics.evaluate()
    assert "snow_depth_m" in diag
