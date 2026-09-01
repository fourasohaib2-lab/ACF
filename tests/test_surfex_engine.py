"""Unit test suite for ACF SURFEX Operational Subsystem (ACF-HPC-105)."""

import pytest

from acf.surfex import (
    SurfexArchive,
    SurfexDiagnostics,
    SurfexManager,
    SurfexMonitor,
    SurfexRestart,
    SurfexRunner,
    SurfexScheduler,
    SurfexTelemetry,
    SurfexValidator,
    SurfexWorkflow,
)
from acf.surfex.engine import SurfexEngine
from acf.surfex.land_surface import COAST, ISBA, LAKE, RIVER, SEA, TEB
from acf.surfex.snow import CROCUS, SNOWPACK, SnowAssimilation, SnowDiagnostics, SnowForecast
from acf.surfex.soil import Drainage, Groundwater, Runoff, SoilHydrology, SoilMoisture, SoilTemperature
from acf.surfex.urban import BuildingPhysics, RoadTemperature, TownEnergyBalance, UrbanHeatIsland, UrbanHydrology
from acf.surfex.vegetation import Biomass, Canopy, CarbonFlux, LeafAreaIndex, Photosynthesis, RootZone, VegetationModel
from acf.surfex.water import Evaporation, Evapotranspiration, LakeModel, RiverRouting, SurfaceFluxes


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


def test_surfex_schemes_no_longer_claim_fabricated_success():
    """
    CORRECTED: every scheme's run()/solve() used to unconditionally
    return True, with no real dynamic-core solver connected anywhere
    in this package. See land_surface/, snow/, urban/, soil/,
    vegetation/, water/'s NOTE (correction) docstrings.
    """
    for scheme in (ISBA, TEB, SEA, LAKE, RIVER, COAST):
        assert scheme.run() is False
    assert CROCUS.run() is False
    assert SNOWPACK.run() is False
    assert SnowAssimilation.assimilate() is False
    assert SnowForecast.predict() is False
    assert TownEnergyBalance.solve() is False
    assert BuildingPhysics.solve() is False
    assert RiverRouting.route() is False
    assert LakeModel.solve() is False
    assert SoilHydrology.solve() is False
    assert SoilTemperature.solve() is False
    assert VegetationModel.run() is False


def test_surfex_fabricated_numeric_results_now_raise_instead_of_lying():
    """
    CORRECTED: every one of these used to unconditionally return the
    exact same fixed, plausible-looking number regardless of any real
    physics solver being connected (e.g. SnowDiagnostics.evaluate()
    always claimed {'snow_depth_m': 0.45, 'swe_mm': 120.0}). They now
    honestly refuse to fabricate a result instead of silently lying.
    """
    for fn in (
        SnowDiagnostics.evaluate,
        UrbanHeatIsland.intensity,
        RoadTemperature.solve,
        UrbanHydrology.runoff,
        Evaporation.solve,
        Evapotranspiration.solve,
        SurfaceFluxes.compute,
        SoilMoisture.evaluate,
        Drainage.rate,
        Runoff.surface,
        Groundwater.recharge,
        LeafAreaIndex.calculate,
        RootZone.depth,
        Canopy.interception,
        Biomass.total,
        Photosynthesis.gpp,
        CarbonFlux.nee,
        SurfexTelemetry().get_metrics,
        SurfexDiagnostics.compute,
        SurfexScheduler().schedule,
    ):
        with pytest.raises(NotImplementedError):
            fn()


def test_surfex_package_wrapper_classes_no_longer_claim_fabricated_success():
    """
    CORRECTED: SurfexRunner/Workflow/Manager/Validator/Archive/Restart
    used to unconditionally return True, and SurfexMonitor.check()
    always claimed "RUNNING" - even for a job that failed, finished,
    or was never submitted. See surfex/__init__.py's NOTE (correction).
    """
    assert SurfexRunner().run() is False
    assert SurfexWorkflow().run() is False
    assert SurfexManager().execute() is False
    assert SurfexValidator().validate() is False
    assert SurfexArchive.archive() is False
    assert SurfexRestart.checkpoint() is False
    assert SurfexMonitor().check() == "UNKNOWN_NO_REAL_MONITORING_CONNECTED"
