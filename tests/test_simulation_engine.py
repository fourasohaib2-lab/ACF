"""Unit test suite for ACF-DT-003 Planetary Simulation Engine."""

import os
import tempfile

import numpy as np
import pytest

from acf.ai.simulation.neural_operator import AIFrameworkType, NeuralOperatorEngine
from acf.hpc.simulation.checkpoint import CheckpointManager
from acf.hpc.simulation.cuda_kernels import CUDAKernelManager
from acf.hpc.simulation.gpu_solver import GPUSolver
from acf.hpc.simulation.mpi_domain import MPIDomainDecomposition
from acf.simulation_engine.atmosphere_solver.atmospheric_model import AtmosphericModel
from acf.simulation_engine.atmosphere_solver.convection_engine import ConvectionEngine, ConvectionScheme
from acf.simulation_engine.atmosphere_solver.microphysics_engine import MicrophysicsEngine
from acf.simulation_engine.climate_scenarios.cmip6 import CMIP6Engine, SSPScenario
from acf.simulation_engine.climate_scenarios.ssp_engine import SSPEngine
from acf.simulation_engine.coupled_solver.coupled_earth_solver import CoupledEarthSolver
from acf.simulation_engine.ensemble_prediction.ensemble_engine import EarthEnsembleEngine
from acf.simulation_engine.ensemble_prediction.probability_engine import ProbabilityEngine
from acf.simulation_engine.extreme_events.cyclone import CycloneSimulator
from acf.simulation_engine.extreme_events.flood import FloodSimulator
from acf.simulation_engine.extreme_events.storm import SevereStormSimulator
from acf.simulation_engine.extreme_events.wildfire import WildfireSimulator
from acf.simulation_engine.land_solver.carbon_flux import CarbonFluxModel
from acf.simulation_engine.land_solver.soil_model import SoilModel
from acf.simulation_engine.land_solver.vegetation_model import VegetationModel
from acf.simulation_engine.numerical_core.adaptive_mesh_refinement import AdaptiveMeshRefinement
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid, GridResolution
from acf.simulation_engine.numerical_core.finite_volume_solver import FiniteVolumeSolver
from acf.simulation_engine.numerical_core.spectral_solver import SpectralSolver
from acf.simulation_engine.ocean_solver.ocean_model import OceanModel
from acf.simulation_engine.ocean_solver.wave_model import WaveModel
from acf.simulation_engine.output.netcdf_writer import NetcdfWriter
from acf.simulation_engine.output.zarr_writer import ZarrWriter


def test_earth_grid():
    grid = EarthGrid(n_lat=18, n_lon=36, n_levels=8, resolution=GridResolution.GLOBAL_NWP_25KM)
    assert grid.n_lat == 18
    assert grid.n_lon == 36
    assert grid.n_levels == 8
    areas = grid.compute_cell_areas()
    assert areas.shape == (18, 36)
    assert np.all(areas > 0)
    p_3d = grid.compute_vertical_pressure_profile(np.full((18, 36), 101325.0))
    assert p_3d.shape == (8, 18, 36)


def test_finite_volume_solver():
    grid = EarthGrid(n_lat=10, n_lon=20, n_levels=4)
    solver = FiniteVolumeSolver(grid)
    is_stable, cfl = solver.check_cfl_condition(max_velocity=50.0, dt=10.0)
    assert is_stable is True
    assert cfl > 0.0

    state = np.ones((10, 20))
    next_state = solver.step(state, dt=1.0)
    assert next_state.shape == (10, 20)
    mass_dev = solver.verify_mass_conservation(state, next_state)
    assert mass_dev < 1e-4


def test_spectral_solver():
    grid = EarthGrid(n_lat=16, n_lon=32, n_levels=4)
    spectral = SpectralSolver(grid)
    u = np.ones((16, 32)) * 10.0
    v = np.ones((16, 32)) * 2.0
    zeta = spectral.compute_vorticity(u, v)
    assert zeta.shape == (16, 32)
    psi = spectral.solve_streamfunction(zeta)
    assert psi.shape == (16, 32)
    c_phase = spectral.rossby_dispersion(zonal_mean_u=20.0, wavenumber_k=1e-6, wavenumber_l=1e-6)
    assert isinstance(c_phase, float)


def test_adaptive_mesh_refinement():
    grid = EarthGrid(n_lat=10, n_lon=20, n_levels=4)
    amr = AdaptiveMeshRefinement(grid)
    p = np.random.normal(100000, 1000, size=(10, 20))
    t = np.random.normal(288, 5, size=(10, 20))
    vort = np.random.normal(0, 1e-4, size=(10, 20))
    mask = amr.evaluate_refinement_masks(p, t, vort)
    assert mask.shape == (10, 20)
    bounds = amr.get_refined_subgrid_bounds(mask)
    assert isinstance(bounds, list)


def test_atmospheric_model():
    grid = EarthGrid(n_lat=10, n_lon=20, n_levels=4)
    model = AtmosphericModel(grid)
    state = model.initialize_state()
    assert "T" in state and "U" in state
    next_state = model.step(state, dt=10.0)
    assert next_state["T"].shape == state["T"].shape


def test_convection_engine():
    engine = ConvectionEngine(scheme=ConvectionScheme.KAIN_FRITSCH)
    t_prof = np.linspace(290, 210, 10)
    p_prof = np.linspace(100000, 20000, 10)
    q_prof = np.full(10, 0.01)
    cape, cin, _lfc, _el = engine.calculate_cape_cin(t_prof, p_prof, q_prof)
    assert cape >= 0.0 and cin >= 0.0

    cape_2d = np.full((5, 5), 1500.0)
    cin_2d = np.full((5, 5), 20.0)
    out = engine.compute_convective_mass_flux(cape_2d, cin_2d)
    assert "mass_flux" in out and out["mass_flux"].shape == (5, 5)


def test_microphysics_engine():
    micro = MicrophysicsEngine()
    hydros = micro.initialize_hydrometeors((4, 10, 10))
    density = np.full((4, 10, 10), 1.2)
    lwc, _iwc = micro.compute_water_content(hydros, density)
    assert lwc.shape == (4, 10, 10)
    temp = np.full((4, 10, 10), 280.0)
    q_vap = np.full((4, 10, 10), 0.005)
    updated_h, _updated_q = micro.step(hydros, temp, q_vap, density, dt=60.0)
    assert "qc" in updated_h


def test_ocean_and_wave_model():
    grid = EarthGrid(n_lat=10, n_lon=20, n_levels=4)
    ocean = OceanModel(grid)
    ostate = ocean.initialize_state()
    assert "SST" in ostate
    next_o = ocean.step(ostate, dt=60.0)
    assert "SST" in next_o

    wave = WaveModel()
    wind = np.full((10, 20), 15.0)
    wave_out = wave.compute_significant_wave_height(wind)
    assert wave_out["Hs"].shape == (10, 20)
    assert np.all(wave_out["Hs"] > 0)


def test_land_and_carbon_models():
    soil = SoilModel()
    sstate = soil.initialize_soil_state((10, 20))
    next_s = soil.step(sstate, np.full((10, 20), 1e-6), np.full((10, 20), 1e-7), np.full((10, 20), 290.0))
    assert "soil_moisture" in next_s

    veg = VegetationModel()
    v_out = veg.compute_vegetation_indices(np.full((10, 20), 295.0), np.full((10, 20), 0.3), np.full((10, 20), 400.0))
    assert "LAI" in v_out and v_out["LAI"].shape == (10, 20)

    carbon = CarbonFluxModel()
    c_out = carbon.compute_carbon_fluxes(420.0, v_out["NPP"], np.full((10, 20), 290.0))
    assert "NEE" in c_out


def test_coupled_earth_solver():
    grid = EarthGrid(n_lat=10, n_lon=20, n_levels=4)
    coupled = CoupledEarthSolver(grid)
    cstate = coupled.initialize_coupled_state()
    assert "T" in cstate and "SST" in cstate and "Soil" in cstate
    next_cstate = coupled.step(cstate, dt=10.0)
    assert "T" in next_cstate and "Carbon_NEE" in next_cstate


def test_ensemble_and_probability_engine():
    grid = EarthGrid(n_lat=10, n_lon=20, n_levels=4)
    solver = CoupledEarthSolver(grid)
    ens = EarthEnsembleEngine(solver, n_members=4)
    base = solver.initialize_coupled_state()
    members = ens.generate_perturbed_initial_states(base)
    assert len(members) == 4
    stats = ens.compute_ensemble_statistics(members, field_key="SST")
    assert "mean" in stats and stats["mean"].shape == (10, 20)

    prob_eng = ProbabilityEngine()
    fields = [m["SST"] for m in members]
    p_exceed = prob_eng.compute_exceedance_probability(fields, threshold=15.0)
    assert p_exceed.shape == (10, 20)


def test_extreme_events():
    cyc = CycloneSimulator()
    slp = np.random.normal(1013, 20, size=(10, 20))
    lats = np.linspace(-40, 40, 10)
    lons = np.linspace(-180, 180, 20)
    diag = cyc.detect_cyclone_center(slp, lats, lons)
    assert "P_min_hpa" in diag

    storm = SevereStormSimulator()
    s_out = storm.evaluate_severe_storm_risk(
        cape=np.full((10, 20), 2000.0),
        srh_03km=np.full((10, 20), 200.0),
        bulk_shear_06km=np.full((10, 20), 25.0),
        cin=np.full((10, 20), 10.0),
    )
    assert "SCP" in s_out and "STP" in s_out

    flood = FloodSimulator()
    f_out = flood.simulate_inundation(
        rainfall_rate_mm_h=np.full((10, 20), 50.0),
        soil_moisture=np.full((10, 20), 0.4),
        elevation_m=np.full((10, 20), 10.0),
    )
    assert "inundation_depth_m" in f_out

    wild = WildfireSimulator()
    w_out = wild.compute_fire_weather_index(
        temp_c=np.full((10, 20), 35.0),
        relative_humidity_pct=np.full((10, 20), 15.0),
        wind_speed_kmh=np.full((10, 20), 40.0),
        rain_24h_mm=np.full((10, 20), 0.0),
    )
    assert "FWI" in w_out


def test_cmip6_and_ssp_engines():
    cmip = CMIP6Engine(SSPScenario.SSP5_85)
    ghg = cmip.get_ghg_concentrations(2050)
    assert ghg["CO2_ppm"] > 415.0

    ssp = SSPEngine(SSPScenario.SSP2_45)
    horiz = ssp.evaluate_horizon(2100)
    assert horiz["global_temp_anomaly_c"] > 0.0


def test_output_writers():
    with tempfile.TemporaryDirectory() as tmpdir:
        nc_path = os.path.join(tmpdir, "test.nc")
        writer = NetcdfWriter(nc_path)
        state = {"T": np.zeros((10, 20)), "P": np.ones((5, 10, 20))}
        lats = np.linspace(-90, 90, 10)
        lons = np.linspace(-180, 180, 20)
        levels = np.arange(5)
        saved_nc = writer.write_state(state, lats, lons, levels)
        assert os.path.exists(saved_nc)

        zarr_path = os.path.join(tmpdir, "test.zarr")
        zwriter = ZarrWriter(zarr_path)
        saved_zarr = zwriter.write_zarr(state, lats, lons, levels)
        assert os.path.exists(saved_zarr)


def test_zarr_writer_propagates_genuine_write_failures(tmp_path, monkeypatch):
    """
    CORRECTED: write_zarr() used to catch bare `Exception` (redundant
    with the ImportError case it also listed) around ds.to_zarr(), so
    ANY real write failure - a bad state array, a genuine xarray/zarr
    bug, disk issues - was silently swallowed and replaced with a fake
    empty store (just {"zarr_format": 2}, no data) while still
    returning the path as if the write had succeeded. Only the true
    "optional zarr backend not installed" case (ImportError) should
    trigger that metadata-only fallback; anything else must propagate.
    """
    import xarray as xr

    from acf.simulation_engine.output.zarr_writer import ZarrWriter

    def _boom(self, *args, **kwargs):
        raise ValueError("simulated genuine write failure, not a missing dependency")

    monkeypatch.setattr(xr.Dataset, "to_zarr", _boom)

    zwriter = ZarrWriter(str(tmp_path / "test.zarr"))
    state = {"T": np.zeros((4, 5))}
    lats = np.linspace(-90, 90, 4)
    lons = np.linspace(-180, 180, 5)
    with pytest.raises(ValueError, match="simulated genuine write failure"):
        zwriter.write_zarr(state, lats, lons)


def test_neural_operator():
    neural = NeuralOperatorEngine(AIFrameworkType.FOURIER_NEURAL_OPERATOR)
    state = {"T": np.random.normal(288, 5, size=(10, 20))}
    next_s = neural.predict_next_state(state, dt=3600.0)
    assert next_s["T"].shape == (10, 20)


def test_hpc_modules():
    gpu = GPUSolver(use_gpu=False)
    a = np.ones((4, 4))
    b = np.ones((4, 4))
    c = gpu.accelerated_matmul(a, b)
    assert c.shape == (4, 4)

    mpi = MPIDomainDecomposition(global_nlat=72, global_nlon=144, n_proc_lat=2, n_proc_lon=4, rank=0)
    bounds = mpi.get_local_bounds()
    assert bounds == (0, 36, 0, 36)

    # CORRECTED: exchange_halo_boundaries() used to silently return
    # local_array.copy() - a no-op claiming to be a real inter-rank
    # halo exchange while never touching the ghost cells or
    # communicating with any other rank. No MPI library is connected
    # in this codebase, so it now raises instead of silently returning
    # wrong boundary data.
    with pytest.raises(NotImplementedError):
        mpi.exchange_halo_boundaries(np.ones((10, 10)))

    cuda = CUDAKernelManager()
    u = np.ones((10, 10))
    v = np.zeros((10, 10))
    sc = np.arange(100).reshape(10, 10).astype(float)
    sc_next = cuda.dispatch_advection_kernel(u, v, sc, dt=0.1)
    assert sc_next.shape == (10, 10)

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_mgr = CheckpointManager(checkpoint_dir=tmpdir)
        saved_file = ckpt_mgr.save_checkpoint(state={"T": 288.0}, step=42)
        assert os.path.exists(saved_file)
        loaded = ckpt_mgr.load_checkpoint(saved_file)
        assert loaded["step"] == 42
